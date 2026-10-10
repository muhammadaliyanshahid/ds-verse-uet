from django import forms
from apps.papers.models import PastPaper, Course, validate_pdf_file
from apps.timetable.models import Semester

class PastPaperUploadForm(forms.ModelForm):
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        empty_label="Select Course",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    semester = forms.ModelChoiceField(
        queryset=Semester.objects.all(),
        empty_label="Select Academic Semester",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    exam_type = forms.ChoiceField(
        choices=PastPaper.EXAM_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    year = forms.IntegerField(
        initial=2025,
        min_value=2015,
        max_value=2030,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2024'})
    )
    uploader_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Ali Raza or 2023-DS-12'}),
        help_text="Your name or Roll Number (Optional)."
    )
    file = forms.FileField(
        validators=[validate_pdf_file],
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
        help_text="Only PDF files are permitted. Max file size: 10 MB."
    )

    class Meta:
        model = PastPaper
        fields = ['course', 'semester', 'exam_type', 'year', 'uploader_name', 'file']
