from django.db import models
from django.contrib.auth.models import User

class StudentProfile(models.Model):
    """
    Extends built-in Django User for BS Data Science students, senior mentors & administrators.
    """
    ROLE_CHOICES = [
        ('student', 'BS DS Student'),
        ('senior', 'Senior / Alumni Mentor'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='student')
    roll_number = models.CharField(max_length=30, unique=True, help_text="e.g. 2023-DS-15")
    section = models.ForeignKey('timetable.Section', on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    semester_number = models.IntegerField(default=1, help_text="Current enrolled semester number (1-8)")
    batch_year = models.IntegerField(default=2023, help_text="Batch entry year (e.g. 2023)")
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(blank=True, null=True, help_text="Short bio or interest in Data Science")
    
    # Senior Mentor specific fields
    is_approved = models.BooleanField(default=True, help_text="Senior mentor accounts require admin approval")
    linkedin_url = models.URLField(blank=True, null=True, help_text="LinkedIn profile URL")
    expertise = models.CharField(max_length=200, blank=True, null=True, help_text="e.g. Machine Learning, FYPs, Internships")

    def __str__(self):
        full_name = self.user.get_full_name() or self.user.username
        sec_name = self.section.name if self.section else "Unassigned"
        role_disp = self.get_role_display()
        return f"{full_name} ({self.roll_number}) - {role_disp} - Sec: {sec_name}"

    @property
    def is_admin(self):
        """Returns True if the user has administrative/staff control."""
        return self.user.is_staff or self.user.is_superuser

    @property
    def is_senior_mentor(self):
        """Returns True if user is an approved senior mentor or staff."""
        return (self.role == 'senior' and self.is_approved) or self.user.is_staff
