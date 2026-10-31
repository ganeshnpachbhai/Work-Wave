from django import forms
from .models import Job

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            "title",
            "description",
            "location",
            "job_type",
            "salary_min",
            "salary_max",
            "deadline",
        ]
        widgets = {
            "description":forms.Textarea(attrs={"rows":5}),
            "deadline":forms.DateInput(
                attrs={"type":"date"},
                format = "%Y-%m-%d",
            ),
        }
    def clean(self):
        cleaned_data = super().clean()
        minimum = cleaned_data.get("salary_min")
        maximum = cleaned_data.get("salary_max")

        if(
            minimum is not None and maximum is not None and minimum > maximum
        ):
            raise forms.ValidationError(
                "Maximum salary must be at least the minimum salary."
            )
        return cleaned_data
    