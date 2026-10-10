from django.contrib import admin
from apps.timetable.models import Semester, Section, TimetableEntry

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current',)
    search_fields = ('name',)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'semester', 'batch_year')
    list_filter = ('semester', 'batch_year')
    search_fields = ('name',)


@admin.register(TimetableEntry)
class TimetableEntryAdmin(admin.ModelAdmin):
    list_display = ('section', 'day_of_week', 'time_slot', 'course', 'room', 'instructor_name')
    list_filter = ('section', 'day_of_week', 'course')
    search_fields = ('course__code', 'course__title', 'instructor_name', 'room')

    def time_slot(self, obj):
        return f"{obj.start_time.strftime('%I:%M %p')} - {obj.end_time.strftime('%I:%M %p')}"
    time_slot.short_description = 'Class Time'
