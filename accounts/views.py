from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from .forms import *
from .models import CustomUser
from django.contrib.auth import logout
from .decorators import role_required
from django.contrib import messages
from hospitals.models import Hospital
from django.urls import reverse


User = get_user_model()

# Patient self-registration
def register_patient(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('accounts:patient_dashboard')
    else:
        form = PatientRegistrationForm()
    return render(request, 'accounts/register_patient.html', {'form': form})

# Admin creates Admin or Staff
@role_required('Admin')
def create_admin_or_staff(request):
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return render(
                request,
                "accounts/create_admin_or_staff.html",
                {
                    "form": AdminUserCreationForm(),  # reset form
                    "account_created": True,
                    "redirect_url": reverse("accounts:admin_dashboard"),
                }
            )
    else:
        form = AdminUserCreationForm()

    return render(request, 'accounts/create_admin_or_staff.html', {'form': form})


@role_required('Admin')
def create_patient(request):
    if request.method == 'POST':
        form = PatientUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return render(
                request,
                "accounts/create_patient.html",
                {
                    "form": PatientUserCreationForm(),  # reset form
                    "account_created": True,
                    "redirect_url": reverse("accounts:admin_dashboard"),
                }
            )
    else:
        form = PatientUserCreationForm()

    return render(request, 'accounts/create_patient.html', {'form': form})

@role_required('Admin')
def user_list(request):
    hospital_id = request.GET.get('hospital_id')

    if not hospital_id:
        # default to first hospital if none provided
        first_hospital = Hospital.objects.first()
        if first_hospital:
            return redirect(f"{reverse('accounts:user_list')}?hospital_id={first_hospital.id}")

    users = User.objects.all().order_by('role', 'email')
    hospital = None

    if hospital_id:
        users = users.filter(hospital_id=hospital_id)
        hospital = Hospital.objects.filter(pk=hospital_id).first()

    return render(request, 'accounts/user_list.html', {
        'users': users,
        'hospital': hospital
    })


# Login
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next') or request.POST.get('next')
                if next_url and next_url.startswith('/') and not next_url.startswith('//'):
                    return redirect(next_url)
                if user.role == 'Admin' or user.is_superuser:
                    return redirect('accounts:admin_dashboard')
                elif user.role == 'Staff':
                    return redirect('accounts:staff_dashboard')
                elif user.role == 'Patient':
                    return redirect('accounts:patient_dashboard')
                return redirect('accounts:login')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

# Logout
def user_logout(request):
    logout(request)
    return redirect('accounts:login')

# Profile Update
@role_required('Admin')
def profile_update(request, pk):
    user_obj = get_object_or_404(CustomUser, pk=pk)
    form = UserProfileForm(request.POST or None, instance=user_obj)

    if request.method == 'POST' and form.is_valid():
        form.save()
        # redirect to the user list for the same hospital
        if user_obj.hospital:
            return redirect(f"{reverse('accounts:user_list')}?hospital_id={user_obj.hospital.id}")
        return redirect('accounts:user_list')

    return render(request, 'accounts/profile_form.html', {
        'form': form,
        'edit_user': user_obj
    })

@role_required('Admin')
def admin_dashboard(request):
    hospitals = Hospital.objects.all().order_by("name")  # keep it neat

    # attach recent users per hospital
    for hospital in hospitals:
        hospital.recent_users = (
            User.objects.filter(hospital=hospital)
            .order_by("-date_joined")[:5]
        )

    return render(request, "dashboard/dashboard_admin.html", {
        "hospitals": hospitals,
    })


@role_required('Staff')
def staff_dashboard(request):
    hospital = request.user.hospital  # full hospital object
    return render(request, 'dashboard/dashboard_staff.html', {'hospital': hospital})

@role_required('Patient')
def patient_dashboard(request):
    hospital = request.user.hospital  # full hospital object
    return render(request, 'dashboard/dashboard_patient.html', {'hospital': hospital})
