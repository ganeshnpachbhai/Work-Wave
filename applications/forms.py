from django import forms
from .models import Application
from workwave.validators import validate_resume_file


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["resume", "cover_letter"]
        widgets = {
            "cover_letter": forms.Textarea(attrs={"rows": 5}),
        }

    def clean_resume(self):
        resume = self.cleaned_data.get("resume")
        if resume:
            validate_resume_file(resume)
        return resume
