from django.shortcuts import render, get_object_or_404, redirect
from .models import Report
from .forms import ReportForm
from accounts.decorators import role_required
from django.contrib.auth.decorators import login_required
from hospitals.models import Hospital
from django.contrib import messages
from django.urls import reverse

# =======================
# REPORT LIST
# =======================
@role_required('Admin', 'Staff')
def report_list(request):
    hospital = None

    if request.user.role == 'Staff':
        hospital = request.user.hospital
        reports = Report.objects.filter(hospital=hospital)
    elif request.user.role == 'Admin':
        hospital_id = request.GET.get('hospital_id')
        if hospital_id:
            hospital = get_object_or_404(Hospital, id=hospital_id)
            reports = Report.objects.filter(hospital=hospital)
        else:
            reports = Report.objects.all()
    else:
        reports = Report.objects.none()

    return render(request, 'reports/report_list.html', {
        'reports': reports,
        'hospital': hospital
    })


# =======================
# REPORT CREATE
# =======================
@role_required('Admin', 'Staff')
def report_create(request):
    if request.user.role == 'Staff':
        hospital = request.user.hospital
    else:  # Admin
        hospital_id = request.GET.get("hospital_id")
        if not hospital_id:
            messages.error(request, "Hospital ID is required to create a report.")
            return redirect("reports:report_list")
        hospital = get_object_or_404(Hospital, id=hospital_id)

    if request.method == "POST":
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.hospital = hospital
            report.generated_by = request.user  # ✅ auto-assign
            report.save()
            messages.success(request, "Report created successfully.")

            if request.user.role == "Admin":
                return redirect(f"{reverse('reports:report_list')}?hospital_id={hospital.id}")
            return redirect('reports:report_list')
    else:
        form = ReportForm()

    return render(request, "reports/report_form.html", {
        "form": form,
        "hospital": hospital
    })


@role_required('Admin', 'Staff')
def report_update(request, pk):
    report = get_object_or_404(Report, pk=pk)

    # Determine hospital context
    if request.user.role == 'Staff':
        if report.hospital != request.user.hospital:
            messages.error(request, "You cannot edit reports from another hospital.")
            return redirect('reports:report_list')
        hospital = request.user.hospital
    else:  # Admin
        hospital_id = request.GET.get("hospital_id")
        if hospital_id:
            hospital = get_object_or_404(Hospital, id=hospital_id)
        else:
            hospital = report.hospital  # fallback

    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES, instance=report)
        if form.is_valid():
            updated_report = form.save(commit=False)
            updated_report.hospital = hospital
            updated_report.generated_by = request.user  # ✅ ensure always set
            updated_report.save()
            messages.success(request, "Report updated successfully.")

            if request.user.role == 'Admin':
                return redirect(f"{reverse('reports:report_list')}?hospital_id={hospital.id}")
            return redirect('reports:report_list')
    else:
        form = ReportForm(instance=report)

    return render(request, 'reports/report_form.html', {
        'form': form,
        'hospital': hospital
    })



# =======================
# REPORT DELETE
# =======================
@role_required('Admin', 'Staff')
def report_delete(request, pk):
    report = get_object_or_404(Report, pk=pk)

    # Determine hospital context
    if request.user.role == 'Staff':
        if report.hospital != request.user.hospital:
            messages.error(request, "You cannot delete reports from another hospital.")
            return redirect('reports:report_list')
        hospital = request.user.hospital
    else:  # Admin
        hospital_id = request.GET.get("hospital_id")
        if hospital_id:
            hospital = get_object_or_404(Hospital, id=hospital_id)
        else:
            hospital = report.hospital

    if request.method == 'POST':
        report.delete()
        # Redirect preserving hospital context for admin
        if request.user.role == 'Admin' and hospital:
            return redirect(f"{reverse('reports:report_list')}?hospital_id={hospital.id}")
        return redirect('reports:report_list')

    return render(request, 'reports/report_confirm_delete.html', {
        'report': report,
        'hospital': hospital
    })
