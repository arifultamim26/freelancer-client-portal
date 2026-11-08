from django import forms
from .models import Feedback


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ("milestone", "message")
        widgets = {"message": forms.Textarea(attrs={"rows": 4, "placeholder": "Share a clear note or question…"})}

    def __init__(self, *args, project, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["milestone"].queryset = project.milestones.all()
        self.fields["milestone"].required = False
