import os
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

def validate_pdf_file(value):
    """Validate that uploaded file is a PDF and under 10MB."""
    ext = os.path.splitext(value.name)[1]
    if ext.lower() != '.pdf':
        raise ValidationError('Invalid file format. Only PDF files are allowed.')
    
    max_size = 10 * 1024 * 1024  # 10MB limit
    if value.size > max_size:
        raise ValidationError(f'File size exceeds the 10 MB limit (Current: {round(value.size / (1024*1024), 2)} MB).')

class Course(models.Model):
    """
    Course curriculum details.
    """
    code = models.CharField(max_length=20, unique=True, help_text="e.g. DS-501")
    title = models.CharField(max_length=150, help_text="e.g. Machine Learning")
    credit_hours = models.IntegerField(default=3)
    semester_number = models.IntegerField(default=1, help_text="Semester number (1-8)")
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['semester_number', 'code']

    def __str__(self):
        return f"{self.code}: {self.title}"


class PastPaper(models.Model):
    """
    Past Paper model uploaded by students (no login required) and approved by faculty/admins.
    """
    EXAM_CHOICES = [
        ('mid', 'Midterm Examination'),
        ('final', 'Final Term Examination'),
        ('quiz', 'Quiz / Sessional'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='past_papers')
    semester = models.ForeignKey('timetable.Semester', on_delete=models.CASCADE, related_name='past_papers')
    uploader = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_papers')
    uploader_name = models.CharField(max_length=100, blank=True, null=True, help_text="Name of student uploader (if unauthenticated)")
    
    exam_type = models.CharField(max_length=10, choices=EXAM_CHOICES)
    year = models.IntegerField(default=2025, help_text="Year exam took place (e.g. 2024)")
    file = models.FileField(upload_to='past_papers/', validators=[validate_pdf_file])
    upload_date = models.DateTimeField(auto_now_add=True)
    
    is_approved = models.BooleanField(default=False, db_index=True, help_text="Requires faculty or student-admin approval")
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_papers')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    download_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-upload_date']

    def __str__(self):
        return f"{self.course.code} - {self.get_exam_type_display()} ({self.year})"

    def get_uploader_display_name(self):
        if self.uploader:
            return self.uploader.get_full_name() or self.uploader.username
        if self.uploader_name:
            return self.uploader_name
        return "Student Contributor"

    def upvotes_count(self):
        return self.ratings.count()

    def is_upvoted_by(self, user):
        if not user.is_authenticated:
            return False
        return self.ratings.filter(student=user).exists()


class PaperRating(models.Model):
    """
    Upvote / rating per student per past paper.
    """
    paper = models.ForeignKey(PastPaper, on_delete=models.CASCADE, related_name='ratings')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='paper_ratings')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('paper', 'student')

    def __str__(self):
        return f"Upvote by {self.student.username} on {self.paper}"
