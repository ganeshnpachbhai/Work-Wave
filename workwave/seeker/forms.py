import re
from django import forms
from .models import (SeekerProfile, Skill)


_INPUT = (
    "w-full rounded-xl border border-[#E5E5E0] px-3.5 py-2.5 text-xs sm:text-sm "
    "focus:outline-none focus:ring-2 focus:ring-[#4357FF] focus:border-[#4357FF] "
    "bg-[#F7F7F2] focus:bg-white text-[#171717] placeholder-[#A3A39C] transition-colors"
)
_SELECT = (
    "w-full rounded-xl border border-[#E5E5E0] px-3.5 py-2.5 text-xs sm:text-sm "
    "focus:outline-none focus:ring-2 focus:ring-[#4357FF] focus:border-[#4357FF] "
    "bg-[#F7F7F2] focus:bg-white text-[#171717] transition-colors"
)
_TEXTAREA = _INPUT + " resize-none"


class SeekerProfileForm(forms.ModelForm):
    skills_text = forms.CharField(required=False, label="Skills", widget=forms.TextInput(
        attrs={
            "placeholder": "e.g. Python, Django, React, AWS, Kubernetes",
            "class": _INPUT,
        }
    ),
        help_text="Separate multiple technical competencies with commas. Maximum 50 characters per skill.",)

    class Meta:
        model = SeekerProfile
        fields = ["full_name",
                  "phone",
                  "location",
                  "headline",
                  "bio",
                  "profile_photo",
                  "resume",]
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "eg. Alex Deo", 'class': _INPUT}),
            "phone": forms.TextInput(attrs={"placeholder": "eg. +91XXXXXXXXXX", "class": _INPUT}),
            "location": forms.TextInput(attrs={"placeholder": "eg.Haidrabad, India or Remote", "class": _INPUT}),
            "headline": forms.TextInput(attrs={"placeholder": "e.g. Senior Backend Engineer & Distributed Systems Lead", "class": _INPUT}),
            "bio": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Summary of your engineering philosophy, architecture experience, and past systems scaled...",
                "class": _TEXTAREA,
            }),
            "profile_photo": forms.ClearableFileInput(attrs={
                "class": "text-xs text-[#525252] file:mr-3 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-bold file:bg-[#F0F2FF] file:text-[#4357FF] hover:file:bg-[#E4E7FF] cursor-pointer"
            }),
            "resume": forms.ClearableFileInput(attrs={
                "class": "text-xs text-[#525252] file:mr-3 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-bold file:bg-[#F6FFCC] file:text-[#171717] hover:file:bg-[#D7FF64] cursor-pointer"
            }),

        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            existing = self.instance.skills.values_list("name", flat=True)
            self.fields["skills_text"].initial = ", ".join(existing)

    # Validation

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        if phone and not re.fullmatch(r"\+?\d{10,15}", phone):
            raise forms.ValidationError(
                "Phone number must be between 10-15 digits, with optional leading '+'."
            )
        return phone

    def clean_profile_photo(self):
        photo = self.cleaned_data.get("profile_photo")
        if photo and hasattr(photo, "content_type"):
            allowed = ("image/jpeg", "image/png", "image/gif", "image/webp")
            if photo.content_type not in allowed:
                raise forms.ValidationError(
                    "Only standard image formats are permitted (JPG, PNG, GIF, WEBP)."
                )
            if photo.size > 2 * 1024*1024:
                raise forms.ValidationError(
                    "Profile photo size must not exceed 2MB.")
        return photo

    def clean_resume(self):
        resume = self.cleaned_data.get("resume")
        if resume and hasattr(resume, "name"):
            name = resume.name.lower()
            if not (name.endswith(".pdf") or name.endswith(".doc") or name.endswith(".docs")):
                raise forms.ValidationError(
                    "Only PDF, DOC, or DOCX documents are accepted.")
            if resume.size > 5 * 1024*1024:
                raise forms.ValidationError(
                    "Resume file size must not exceed 5MB.")
        return resume

    def clean_skills_text(self):
        raw = self.cleaned_data.get("skills_text", "")
        names = [s.strip().title() for s in raw.split(",") if s.strip()]
        for name in names:
            if len(name) > 50:
                raise forms.ValidationError(
                    f"Skill name '{name}' exceeds 50 characters maximum length.")
        return names

    def save(self, commit=True):
        profile = super().save(commit=commit)
        if commit:
            skills_name = self.cleaned_data.get("skills_text", [])
            skills = []
            for name in skills_name:
                skill, _ = Skill.objects.get_or_create(name=name)
                skills.append(skill)
            profile.skills.set(skills)
        return profile
