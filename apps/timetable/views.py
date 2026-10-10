from django.shortcuts import render, get_object_or_404
from django.views import View
from apps.timetable.models import Section, TimetableEntry, Semester
from apps.accounts.models import StudentProfile

class TimetableView(View):
    def get(self, request):
        sections = Section.objects.select_related('semester').all()
        selected_section_id = request.GET.get('section')
        
        selected_section = None
        if selected_section_id:
            selected_section = Section.objects.filter(id=selected_section_id).first()
        
        # If no section selected in GET, check logged-in user profile or pick first section
        if not selected_section:
            if request.user.is_authenticated:
                profile = StudentProfile.objects.filter(user=request.user).first()
                if profile and profile.section:
                    selected_section = profile.section
            
            if not selected_section:
                selected_section = sections.first()

        days = [
            ('MON', 'Monday'),
            ('TUE', 'Tuesday'),
            ('WED', 'Wednesday'),
            ('THU', 'Thursday'),
            ('FRI', 'Friday'),
        ]

        timetable_by_day = {}
        if selected_section:
            entries = TimetableEntry.objects.filter(section=selected_section).select_related('course').order_by('start_time')
            for day_code, day_name in days:
                timetable_by_day[day_name] = entries.filter(day_of_week=day_code)

        return render(request, 'timetable/timetable_grid.html', {
            'sections': sections,
            'selected_section': selected_section,
            'timetable_by_day': timetable_by_day,
            'days': days,
        })
