from django.db import models
from django.contrib.auth.models import User

class SeniorPost(models.Model):
    """
    Guidance posts & articles written by approved Seniors. Requires Admin approval before publishing.
    """
    CATEGORY_CHOICES = [
        ('career', 'Career & Job Opportunities'),
        ('fyp', 'Final Year Project (FYP) Advice'),
        ('courses', 'Course & Study Tips'),
        ('internships', 'Internships & Networking'),
        ('general', 'General Student Guidance'),
    ]

    senior = models.ForeignKey(User, on_delete=models.CASCADE, related_name='senior_posts')
    title = models.CharField(max_length=200, help_text="e.g. How to prepare for Machine Learning FYP")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    content = models.TextField(help_text="Write guidance, advice, or resources for junior students...")
    created_at = models.DateTimeField(auto_now_add=True)

    is_approved = models.BooleanField(default=False, db_index=True, help_text="Requires Admin approval before being displayed to students")
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_senior_posts')
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} by {self.senior.get_full_name() or self.senior.username} ({self.get_category_display()})"


class SeniorQuery(models.Model):
    """
    Queries / Questions submitted by students (guest or logged-in) to Senior Mentors.
    """
    target_senior = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_queries', help_text="Leave blank to send to all Senior Mentors")
    sender_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_queries')
    sender_name = models.CharField(max_length=100, help_text="Name of student or visitor")
    sender_email = models.EmailField(blank=True, null=True, help_text="Optional email for notification")
    
    subject = models.CharField(max_length=200, help_text="Short summary of query/difficulty")
    message = models.TextField(help_text="Detailed query, difficulty, or question...")
    created_at = models.DateTimeField(auto_now_add=True)

    reply = models.TextField(blank=True, null=True, help_text="Response from Senior Mentor")
    replied_at = models.DateTimeField(blank=True, null=True)
    is_answered = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Senior Queries"

    def __str__(self):
        target = self.target_senior.get_full_name() if self.target_senior else "All Seniors"
        return f"Query from {self.sender_name} to {target}: {self.subject}"
