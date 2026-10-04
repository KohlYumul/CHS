from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import PatientProfile, MedicalRecord, Comment
from .forms import MedicalRecordForm, CommentForm, PatientProfileForm
from accounts.decorators import role_required
from django.contrib.auth import get_user_model
from hospitals.models import Hospital
from django.contrib import messages

User = get_user_model()

# =========================
# Medical Record Views
# =========================

@role_required('Admin', 'Staff')
def record_list(request, hospital_id=None):
    """Show medical records based on role."""
    if request.user.role == 'Staff':
        records = MedicalRecord.objects.filter(patient__user__hospital=request.user.hospital)
    elif request.user.role == 'Admin' and hospital_id:
        records = MedicalRecord.objects.filter(patient__user__hospital_id=hospital_id)
    else:
        records = MedicalRecord.objects.all()
    return render(request, 'patients/record_list.html', {
        'records': records,
        'hospital_id': hospital_id if request.user.role == 'Admin' else None
    })


@role_required('Admin', 'Staff')
def record_create(request):
    hospital_id = None
    if request.user.role == 'Admin':
        hospital_id = request.GET.get('hospital_id')

    if request.method == 'POST':
        form = MedicalRecordForm(request.POST, request.FILES)
        if form.is_valid():
            record = form.save(commit=False)
            if request.user.role == 'Staff' and record.patient.user.hospital != request.user.hospital:
                return HttpResponseForbidden("You cannot add records for patients in another hospital.")
            record.save()
            redirect_url = reverse('patients:record_list')
            if request.user.role == 'Admin' and hospital_id:
                redirect_url += f"?hospital_id={hospital_id}"
            return redirect(redirect_url)
    else:
        form = MedicalRecordForm()

    return render(request, 'patients/record_form.html', {
        'form': form,
        'hospital_id': hospital_id
    })


@role_required('Admin', 'Staff')
def record_update(request, pk):
    record = get_object_or_404(MedicalRecord, pk=pk)
    hospital_id = None
    if request.user.role == 'Admin':
        hospital_id = request.GET.get('hospital_id')

    if request.user.role == 'Staff' and record.patient.user.hospital != request.user.hospital:
        return HttpResponseForbidden("You cannot edit records for another hospital.")

    if request.method == 'POST':
        form = MedicalRecordForm(request.POST, request.FILES, instance=record)
        if form.is_valid():
            form.save()
            redirect_url = reverse('patients:record_list')
            if request.user.role == 'Admin' and hospital_id:
                redirect_url += f"?hospital_id={hospital_id}"
            return redirect(redirect_url)
    else:
        form = MedicalRecordForm(instance=record)

    return render(request, 'patients/record_form.html', {
        'form': form,
        'hospital_id': hospital_id
    })


@role_required('Admin', 'Staff')
def record_delete(request, pk):
    record = get_object_or_404(MedicalRecord, pk=pk)
    hospital_id = None
    if request.user.role == 'Admin':
        hospital_id = request.GET.get('hospital_id')

    if request.user.role == 'Staff' and record.patient.user.hospital != request.user.hospital:
        return HttpResponseForbidden("You cannot delete records for another hospital.")

    if request.method == 'POST':
        record.delete()
        redirect_url = reverse('patients:record_list')
        if request.user.role == 'Admin' and hospital_id:
            redirect_url += f"?hospital_id={hospital_id}"
        return redirect(redirect_url)

    return render(request, 'patients/record_confirm_delete.html', {
        'record': record,
        'hospital_id': hospital_id
    })


# =========================
# Comment Views
# =========================

@role_required('Admin', 'Staff', 'Patient')
def comment_create(request, record_id):
    record = get_object_or_404(MedicalRecord, pk=record_id)

    if request.user.role == 'Staff' and record.patient.user.hospital != request.user.hospital:
        return HttpResponseForbidden("You cannot comment on records from another hospital.")
    if request.user.role == 'Patient' and record.patient.user != request.user:
        return HttpResponseForbidden("You cannot comment on another patient's record.")

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.record = record
            comment.author = request.user
            comment.save()

            if request.user.role == 'Patient':
                return redirect('patients:my_record')
            else:
                hospital_id = None
                if request.user.role == 'Admin':
                    hospital_id = request.GET.get('hospital_id')
                redirect_url = reverse('patients:record_list')
                if hospital_id:
                    redirect_url += f"?hospital_id={hospital_id}"
                return redirect(redirect_url)
    else:
        form = CommentForm()

    return render(request, 'patients/comment_form.html', {
        'form': form,
        'record': record
    })


@role_required('Admin', 'Staff', 'Patient')
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)

    if request.user.role == 'Staff' and comment.record.patient.user.hospital != request.user.hospital:
        return HttpResponseForbidden("You cannot delete comments from another hospital.")
    if request.user.role == 'Patient' and comment.author != request.user:
        return HttpResponseForbidden("You cannot delete another user's comment.")

    if request.method == 'POST':
        comment.delete()
        if request.user.role == 'Patient':
            return redirect('patients:my_record')
        else:
            hospital_id = None
            if request.user.role == 'Admin':
                hospital_id = request.GET.get('hospital_id')
            redirect_url = reverse('patients:record_list')
            if hospital_id:
                redirect_url += f"?hospital_id={hospital_id}"
            return redirect(redirect_url)

    return render(request, 'patients/comment_confirm_delete.html', {
        'comment': comment
    })


# =========================
# Patient-Only My Record View
# =========================
@role_required('Patient')
def my_record(request):
    patient_profile = PatientProfile.objects.filter(user=request.user).first()

    if patient_profile:
        records = MedicalRecord.objects.filter(patient=patient_profile)
    else:
        records = []  # No profile means no records

    return render(request, 'patients/my_record.html', {
        'records': records,
        'patient_profile': patient_profile
    })
@role_required('Patient')
def my_profile(request):
    profile = get_object_or_404(PatientProfile, user=request.user)
    return render(request, 'patients/my_profile.html', {'profile': profile})

@role_required('Admin', 'Staff')
def patient_list(request):
    """List patients with hospital scoping like the supply list."""
    hospital = None

    if request.user.role == 'Staff':
        hospital = request.user.hospital
        patients = PatientProfile.objects.filter(user__hospital=hospital)
    elif request.user.role == 'Admin':
        hospital_id = request.GET.get('hospital_id')
        if hospital_id:
            hospital = get_object_or_404(Hospital, id=hospital_id)
            patients = PatientProfile.objects.filter(user__hospital=hospital)
        else:
            patients = PatientProfile.objects.all()

    return render(request, "patients/patient_list.html", {
        'patients': patients,
        'hospital': hospital
    })


@role_required('Admin', 'Staff')
def patient_detail(request, pk):
    """Detailed view of a patient with hospital-aware redirects."""
    patient = get_object_or_404(PatientProfile, pk=pk)
    hospital = patient.user.hospital  # always derive from patient

    # Staff can only access patients from their own hospital
    if request.user.role == "Staff" and hospital != request.user.hospital:
        return redirect("patients:patient_list")

    return render(request, "patients/patient_detail.html", {
        "patient": patient,
        "hospital": hospital,
    })


@role_required('Admin', 'Staff')
def patientprofile_create(request):
    """Create a new patient profile."""
    hospital_id = request.GET.get('hospital_id')  # Admin can pass hospital_id
    if request.method == 'POST':
        form = PatientProfileForm(request.POST, is_update=False)
        if form.is_valid():
            patient_profile = form.save(commit=False)

            # Staff can only assign patients to their own hospital
            if request.user.role == 'Staff':
                patient_profile.user.hospital = request.user.hospital
                patient_profile.user.save()

            patient_profile.save()
            messages.success(request, "Patient profile created successfully.")

            # Redirect back to filtered patient list if Admin
            if request.user.role == 'Admin' and hospital_id:
                return redirect(f"{reverse('patients:patient_list')}?hospital_id={hospital_id}")
            return redirect('patients:patient_list')
    else:
        form = PatientProfileForm(is_update=False)

    return render(request, 'patients/patient_form.html', {
        'form': form,
        'patient': None,
        'hospital_id': hospital_id if request.user.role == 'Admin' else None
    })


@role_required('Admin', 'Staff')
def patientprofile_update(request, pk):
    """Update an existing Patient Profile."""
    patient_profile = get_object_or_404(PatientProfile, pk=pk)
    hospital = patient_profile.user.hospital
    hospital_id = request.GET.get('hospital_id')  # Admin can pass hospital_id

    # Staff can only edit patients from their own hospital
    if request.user.role == "Staff" and hospital != request.user.hospital:
        return HttpResponseForbidden("You cannot edit a patient from another hospital.")

    if request.method == "POST":
        form = PatientProfileForm(request.POST, instance=patient_profile, is_update=True)
        if form.is_valid():
            patient_profile.save()
            messages.success(request, "Patient profile updated successfully.")

            if request.user.role == "Admin" and hospital:
                return redirect(f"{reverse('patients:patient_list')}?hospital_id={hospital.id}")
            return redirect('patients:patient_list')
    else:
        form = PatientProfileForm(instance=patient_profile, is_update=True)

    return render(request, "patients/patient_form.html", {
        "form": form,
        "patient": patient_profile,
        "hospital": hospital,
        "hospital_id": hospital_id if request.user.role == 'Admin' else None
    })