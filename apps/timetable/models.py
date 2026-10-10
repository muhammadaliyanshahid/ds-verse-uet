from django.db import models

class Semester(models.Model):
    """
    Academic Semester representation (e.g. Fall 2025, Spring 2026).
    """
    name = models.CharField(max_length=50, unique=True, help_text="e.g. Fall 2025")
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False, help_text="Mark if this is the active semester")

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.name}{' (Current)' if self.is_current else ''}"

    def save(self, *args, **kwargs):
        if self.is_current:
            # Set all other semesters is_current to False
            Semester.objects.filter(is_current=True).exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)


class Section(models.Model):
    """
    Class Section (e.g. DS-1A, DS-5A).
    """
    name = models.CharField(max_length=20, help_text="e.g. DS-5A")
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='sections')
    batch_year = models.IntegerField(default=2023, help_text="Admission batch year (e.g. 2023)")

    class Meta:
        ordering = ['name']
        unique_together = ('name', 'semester')

    def __str__(self):
        return f"{self.name} ({self.semester.name})"


class TimetableEntry(models.Model):
    """
    Individual class schedule entry for a specific section and course.
    """
    DAY_CHOICES = [
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
    ]

    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='timetable_entries')
    course = models.ForeignKey('papers.Course', on_delete=models.CASCADE, related_name='timetable_entries')
    day_of_week = models.CharField(max_length=3, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50, help_text="e.g. Lab 03, Hall 204")
    instructor_name = models.CharField(max_length=100, help_text="e.g. Dr. Asim Farooq")

    class Meta:
        ordering = ['day_of_week', 'start_time']
        verbose_name_plural = "Timetable Entries"

    def __str__(self):
        return f"{self.section.name} | {self.get_day_of_week_display()} | {self.course.code} ({self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')})"
