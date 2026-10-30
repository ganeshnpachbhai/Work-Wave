"""
WorkWave Security Framework - Secure File Validation.
Enforces strict file extension, MIME type, file size, and path traversal checks.
"""

import os
from django.core.exceptions import ValidationError

ALLOWED_RESUME_EXTENSIONS = {".pdf", ".doc", ".docx"}
ALLOWED_RESUME_MIME_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/octet-stream",
}
MAX_RESUME_SIZE = 5 * 1024 * 1024  # 5 Megabytes

ALLOWED_PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_PHOTO_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}
MAX_PHOTO_SIZE = 2 * 1024 * 1024  # 2 Megabytes


def validate_resume_file(file):
    """
    Validates resume upload against size limits, allowed extensions, and MIME signatures.
    """
    if not file:
        return

    # Path traversal check
    filename = os.path.basename(file.name)
    if ".." in filename or filename.startswith("/") or filename.startswith("\\"):
        raise ValidationError("Invalid filename detected.")

    # Size check
    if file.size > MAX_RESUME_SIZE:
        raise ValidationError(
            f"Resume file size exceeds maximum limit of 5MB (Uploaded: {file.size / (1024 * 1024):.1f}MB)."
        )

    # Extension check
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_RESUME_EXTENSIONS:
        raise ValidationError(
            f"Unsupported file format '{ext}'. Only PDF, DOC, and DOCX files are permitted."
        )

    # MIME / Content-Type check
    content_type = getattr(file, "content_type", None)
    if content_type and content_type.lower() not in ALLOWED_RESUME_MIME_TYPES:
        raise ValidationError(
            f"Invalid file content type '{content_type}' for resume upload."
        )


def validate_profile_photo(file):
    """
    Validates profile photo upload against size limits, allowed extensions, and MIME signatures.
    """
    if not file:
        return

    # Path traversal check
    filename = os.path.basename(file.name)
    if ".." in filename or filename.startswith("/") or filename.startswith("\\"):
        raise ValidationError("Invalid filename detected.")

    # Size check
    if file.size > MAX_PHOTO_SIZE:
        raise ValidationError(
            f"Profile photo exceeds maximum limit of 2MB (Uploaded: {file.size / (1024 * 1024):.1f}MB)."
        )

    # Extension check
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_PHOTO_EXTENSIONS:
        raise ValidationError(
            f"Unsupported image format '{ext}'. Only JPG, JPEG, PNG, and WEBP images are permitted."
        )

    # MIME / Content-Type check
    content_type = getattr(file, "content_type", None)
    if content_type and content_type.lower() not in ALLOWED_PHOTO_MIME_TYPES:
        raise ValidationError(
            f"Invalid image content type '{content_type}' for profile photo."
        )
