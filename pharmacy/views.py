from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.db import transaction
from django.contrib import messages
from django.urls import reverse

from accounts.decorators import role_required
from hospitals.models import Hospital
from inventory.models import Medication
from .models import Prescription, Purchase
from .forms import PrescriptionForm, PurchaseForm

User = get_user_model()


# ==================================
# Medication list for pharmacy (all roles)
# ==================================
@role_required('Admin', 'Staff', 'Patient')
def pharmacy_medication_list(request):
    """Show OTC medications. Staff/Patient see only their hospital. Admin sees all or filtered by optional hospital."""
    if request.user.role == "Admin":
        medications = Medication.objects.filter(prescription_required=False).order_by('name')
        hospital_id = request.GET.get('hospital_id')
        hospital = get_object_or_404(Hospital, id=hospital_id) if hospital_id else None
        if hospital:
            medications = medications.filter(hospital=hospital)
    else:  # Staff or Patient
        hospital = request.user.hospital
        medications = Medication.objects.filter(
            hospital=hospital,
            prescription_required=False
        ).order_by('name')

    return render(request, 'pharmacy/medication_list.html', {
        'medications': medications,
        'hospital': hospital
    })


# ==================================
# Prescribe Medication (Staff/Admin only)
# ==================================
@role_required('Admin', 'Staff')
def prescribe_medication(request):
    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            prescription = form.save(commit=False)

            if request.user.role == 'Staff' and prescription.patient.hospital != request.user.hospital:
                messages.error(request, "You cannot prescribe medication for a patient in another hospital.")
                return redirect('pharmacy:prescribe_medication')

            prescription.prescribed_by = request.user
            prescription.save()
            if request.user.role == 'Admin':
                return redirect('accounts:admin_dashboard')
            return redirect('accounts:staff_dashboard')
    else:
        form = PrescriptionForm()
        if request.user.role == 'Staff':
            form.fields['patient'].queryset = User.objects.filter(
                role='Patient',
                hospital=request.user.hospital
            )
            form.fields['medication'].queryset = Medication.objects.filter(
                hospital=request.user.hospital,
                prescription_required=True,
                quantity__gt=0   # ✅ Only meds with stock
            )
        else:  # Admin
            form.fields['medication'].queryset = Medication.objects.filter(
                prescription_required=True,
                quantity__gt=0   # ✅ Only meds with stock
            )

    return render(request, 'pharmacy/prescription_form.html', {'form': form})



# ==================================
# Buy Medication (Patient)
# ==================================
@role_required('Patient')
@transaction.atomic
def buy_medication(request, medication_id):
    medication = get_object_or_404(Medication, id=medication_id, hospital=request.user.hospital)

    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            qty = form.cleaned_data['quantity']
            med_locked = Medication.objects.select_for_update().get(pk=medication.pk)

            if med_locked.quantity < qty:
                return render(request, 'pharmacy/purchase_denied.html', {
                    'medication': medication,
                    'reason': "Not enough stock available."
                })

            med_locked.quantity -= qty
            med_locked.save()

            Purchase.objects.create(
                patient=request.user,
                medication=medication,
                quantity=qty,
                hospital=med_locked.hospital
            )

            total_price = medication.price * qty
            messages.success(request, f"Successfully purchased {qty} x {medication.name} for ₱{total_price:.2f}.")
            return redirect('pharmacy:medication_list')
    else:
        form = PurchaseForm(initial={'quantity': 1})

    total_price = medication.price * form.initial.get('quantity', 1)
    return render(request, 'pharmacy/purchase_form.html', {
        'medication': medication,
        'form': form,
        'total_price': total_price
    })


# ==================================
# Patient prescription list
# ==================================
@role_required('Patient')
def my_prescriptions(request):
    prescriptions = Prescription.objects.filter(
        patient=request.user,
        medication__hospital=request.user.hospital
    ).order_by('-date_prescribed')

    hospital = request.user.hospital
    return render(request, 'pharmacy/my_prescriptions.html', {
        'prescriptions': prescriptions,
        'hospital': hospital
    })


# ==================================
# Patient purchase history
# ==================================
@role_required('Patient')
def purchase_history(request):
    purchases = Purchase.objects.filter(
        patient=request.user,
        hospital=request.user.hospital
    ).order_by('-date_purchased')

    purchases_with_price = [{
        'medication': p.medication,
        'quantity': p.quantity,
        'price_per_unit': p.medication.price,
        'total_price': p.quantity * p.medication.price,
        'date_purchased': p.date_purchased
    } for p in purchases]

    hospital = request.user.hospital
    return render(request, 'pharmacy/purchase_history.html', {
        'purchases': purchases_with_price,
        'hospital': hospital
    })


# ==================================
# Buy from Prescription (Patient)
# ==================================
@role_required('Patient')
@transaction.atomic
def buy_from_prescription(request, prescription_id):
    # Lock the prescription row for update
    prescription = get_object_or_404(
        Prescription.objects.select_for_update(),
        id=prescription_id,
        patient=request.user,
        is_active=True,
        medication__hospital=request.user.hospital
    )
    medication = prescription.medication
    quantity = prescription.quantity
    total_price = medication.price * quantity

    if request.method == "POST":
        # Lock medication row for update
        med_locked = Medication.objects.select_for_update().get(pk=medication.pk)

        if med_locked.quantity < quantity:
            return render(request, 'pharmacy/purchase_denied.html', {
                'medication': medication,
                'reason': "Not enough stock available."
            })

        # Update medication stock
        med_locked.quantity -= quantity
        med_locked.save()

        # Record purchase
        Purchase.objects.create(
            patient=request.user,
            medication=med_locked,
            quantity=quantity,
            hospital=med_locked.hospital
        )

        # Mark prescription as used
        prescription.is_active = False
        prescription.save()

        # Prepare success message & redirect
        return render(request, 'pharmacy/purchase_from_prescription_confirm.html', {
            'medication': medication,
            'prescription': prescription,
            'total_price': total_price,
            'purchase_success': True,
            'redirect_url': redirect('pharmacy:my_prescriptions').url
        })

    return render(request, 'pharmacy/purchase_from_prescription_confirm.html', {
        'medication': medication,
        'prescription': prescription,
        'total_price': total_price
    })