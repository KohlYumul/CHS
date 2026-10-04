from django.shortcuts import render, get_object_or_404, redirect
from .models import Hospital, Department
from .forms import HospitalForm, DepartmentForm
from accounts.models import CustomUser
from inventory.models import Equipment, MedicalSupply, Medication
from reports.models import Report
from .models import Hospital
from django.shortcuts import render, get_object_or_404
from accounts.decorators import role_required


@role_required('Admin')
def hospital_list_view(request):
    hospitals = Hospital.objects.all()

    context = {
        'hospitals': hospitals
    }
    return render(request, 'hospitals/hospital_list.html', context)


@role_required('Admin')
def hospital_create(request):
    if request.method == 'POST':
        form = HospitalForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('accounts:admin_dashboard')
    else:
        form = HospitalForm()
    return render(request, 'hospitals/hospital_form.html', {'form': form})


@role_required('Admin')
def hospital_update(request, pk):
    hospital = get_object_or_404(Hospital, pk=pk)
    if request.method == 'POST':
        form = HospitalForm(request.POST, instance=hospital)
        if form.is_valid():
            form.save()
            return redirect('accounts:admin_dashboard')
    else:
        form = HospitalForm(instance=hospital)
    return render(request, 'hospitals/hospital_form.html', {'form': form})


@role_required('Admin')
def hospital_delete(request, pk):
    hospital = get_object_or_404(Hospital, pk=pk)
    if request.method == 'POST':
        hospital.delete()
        return redirect('accounts:admin_dashboard')
    return render(request, 'hospitals/hospital_confirm_delete.html', {'hospital': hospital})


@role_required('Admin')
def hospital_overview(request, pk):
    hospital = get_object_or_404(Hospital, pk=pk)

    # Filter users by hospital
    staff_count = CustomUser.objects.filter(role='Staff', hospital=hospital).count()
    patient_count = CustomUser.objects.filter(role='Patient', hospital=hospital).count()

    # Inventory counts per hospital
    equipment_count = Equipment.objects.filter(hospital=hospital).count()
    supply_count = MedicalSupply.objects.filter(hospital=hospital).count()
    medication_count = Medication.objects.filter(hospital=hospital).count()

    # Latest patients for this hospital
    latest_patients = (
        CustomUser.objects.filter(role='Patient', hospital=hospital)
        .order_by('-date_joined')[:5]
    )

    return render(request, 'hospitals/hospital_overview.html', {
        'hospital': hospital,
        'staff_count': staff_count,
        'patient_count': patient_count,
        'equipment_count': equipment_count,
        'supply_count': supply_count,
        'medication_count': medication_count,
        'latest_patients': latest_patients,
    })
