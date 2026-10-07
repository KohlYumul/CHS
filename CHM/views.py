import os
import mimetypes
from pathlib import Path

from django.conf import settings
from django.http import HttpResponseForbidden, Http404, FileResponse
from patients.models import MedicalRecord
from reports.models import Report


def serve_protected_media(request, file_path):
    """
    Serve uploaded media files with strict role-based access control:
    - Anonymous users: 403 Forbidden
    - Patients: Can only access their own medical records
    - Staff: Can only access medical records and reports from their own hospital
    - Admin: Can access all files
    - Path traversal attempts: 403 Forbidden
    """
    if not request.user.is_authenticated:
        return HttpResponseForbidden("You must be logged in to access medical files.")

    # 1. Path normalization and traversal prevention
    media_root = Path(settings.MEDIA_ROOT).resolve()

    # Reject null bytes or suspicious characters
    if '\x00' in file_path:
        return HttpResponseForbidden("Invalid file path.")

    # Normalize relative path (forward slashes for consistent DB lookup)
    clean_relative_path = Path(file_path).as_posix().lstrip('/')
    target_path = (media_root / clean_relative_path).resolve()

    try:
        target_path.relative_to(media_root)
    except ValueError:
        # Path escaped media root
        return HttpResponseForbidden("Access denied: Invalid file path.")

    if not target_path.is_file():
        raise Http404("File not found.")

    user = request.user
    role = getattr(user, 'role', None)
    is_admin = (role == 'Admin') or getattr(user, 'is_superuser', False)

    # 2. Permission checks
    if is_admin:
        pass
    elif clean_relative_path.startswith('medical_records/'):
        # Look up MedicalRecord in DB matching the file path or filename
        record = MedicalRecord.objects.filter(file=clean_relative_path).select_related('patient__user').first()
        if not record:
            filename = Path(clean_relative_path).name
            record = MedicalRecord.objects.filter(file__endswith=filename).select_related('patient__user').first()

        if not record:
            raise Http404("Medical record not found.")

        if role == 'Patient':
            if record.patient.user_id != user.id:
                return HttpResponseForbidden("You are not authorized to view this medical record.")
        elif role == 'Staff':
            patient_hospital = record.patient.user.hospital_id
            if not user.hospital_id or patient_hospital != user.hospital_id:
                return HttpResponseForbidden("You can only view medical records from your hospital.")
        else:
            return HttpResponseForbidden("Access denied.")

    elif clean_relative_path.startswith('reports/'):
        report = Report.objects.filter(file=clean_relative_path).first()
        if not report:
            filename = Path(clean_relative_path).name
            report = Report.objects.filter(file__endswith=filename).first()

        if not report:
            raise Http404("Report not found.")

        if role == 'Staff':
            if not user.hospital_id or report.hospital_id != user.hospital_id:
                return HttpResponseForbidden("You can only view reports from your hospital.")
        else:
            return HttpResponseForbidden("You are not authorized to view hospital reports.")
    else:
        # Any other files require Admin privileges
        return HttpResponseForbidden("Access denied.")


    content_type, _ = mimetypes.guess_type(str(target_path))
    content_type = content_type or 'application/octet-stream'
    return FileResponse(open(target_path, 'rb'), content_type=content_type)

