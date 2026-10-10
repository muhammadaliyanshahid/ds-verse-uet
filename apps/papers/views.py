import os
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from django.http import FileResponse, Http404, JsonResponse, HttpResponseForbidden
from django.utils import timezone
from django.db.models import Q, Count

from apps.papers.models import PastPaper, Course, PaperRating
from apps.papers.forms import PastPaperUploadForm
from apps.timetable.models import Semester, Section, TimetableEntry
from apps.accounts.models import StudentProfile
from apps.seniors.models import SeniorPost

class LandingPageView(View):
    def get(self, request):
        total_papers = PastPaper.objects.filter(is_approved=True).count()
        total_courses = Course.objects.count()
        total_sections = Section.objects.count()
        total_downloads = sum(PastPaper.objects.filter(is_approved=True).values_list('download_count', flat=True)) or 0
        
        recent_papers = PastPaper.objects.filter(is_approved=True).select_related('course', 'semester', 'uploader')[:4]
        
        return render(request, 'landing.html', {
            'total_papers': total_papers,
            'total_courses': total_courses,
            'total_sections': total_sections,
            'total_downloads': total_downloads,
            'recent_papers': recent_papers
        })


class GpaCalculatorView(View):
    """
    Simple GPA Calculator for UET BS Data Science students.
    """
    def get(self, request):
        grade_scale = [
            ('A+', 4.00, '85% - 100%'),
            ('A', 4.00, '80% - 84%'),
            ('A-', 3.70, '75% - 79%'),
            ('B+', 3.30, '70% - 74%'),
            ('B', 3.00, '65% - 69%'),
            ('B-', 2.70, '60% - 64%'),
            ('C+', 2.30, '55% - 59%'),
            ('C', 2.00, '50% - 54%'),
            ('C-', 1.70, '45% - 49%'),
            ('D+', 1.30, '40% - 44%'),
            ('F', 0.00, 'Below 40%'),
        ]
        return render(request, 'gpa/calculator.html', {'grade_scale': grade_scale})


@method_decorator(login_required, name='dispatch')
class DashboardView(View):
    def get(self, request):
        profile, created = StudentProfile.objects.get_or_create(user=request.user)
        student_section = profile.section
        
        weekday_map = {0: 'MON', 1: 'TUE', 2: 'WED', 3: 'THU', 4: 'FRI'}
        today_code = weekday_map.get(timezone.now().weekday(), 'MON')
        
        today_entries = []
        if student_section:
            today_entries = TimetableEntry.objects.filter(
                section=student_section,
                day_of_week=today_code
            ).select_related('course', 'section').order_by('start_time')
        else:
            first_sec = Section.objects.first()
            if first_sec:
                today_entries = TimetableEntry.objects.filter(
                    section=first_sec,
                    day_of_week=today_code
                ).select_related('course', 'section').order_by('start_time')

        semester_papers = PastPaper.objects.filter(is_approved=True).select_related('course', 'semester', 'uploader')[:5]
        
        user_uploads = request.user.uploaded_papers.all()
        pending_count = user_uploads.filter(is_approved=False).count()
        approved_count = user_uploads.filter(is_approved=True).count()

        return render(request, 'dashboard.html', {
            'profile': profile,
            'today_entries': today_entries,
            'today_code_display': dict(TimetableEntry.DAY_CHOICES).get(today_code, 'Today'),
            'semester_papers': semester_papers,
            'pending_count': pending_count,
            'approved_count': approved_count,
        })


class PaperListView(View):
    def get(self, request):
        papers = PastPaper.objects.filter(is_approved=True).select_related('course', 'semester', 'uploader').prefetch_related('ratings')
        
        course_id = request.GET.get('course')
        exam_type = request.GET.get('exam_type')
        semester_id = request.GET.get('semester')
        search_query = request.GET.get('q')

        if course_id:
            papers = papers.filter(course_id=course_id)
        if exam_type:
            papers = papers.filter(exam_type=exam_type)
        if semester_id:
            papers = papers.filter(semester_id=semester_id)
        if search_query:
            papers = papers.filter(
                Q(course__code__icontains=search_query) |
                Q(course__title__icontains=search_query) |
                Q(year__icontains=search_query)
            )

        upvoted_paper_ids = set()
        if request.user.is_authenticated:
            upvoted_paper_ids = set(
                PaperRating.objects.filter(student=request.user).values_list('paper_id', flat=True)
            )

        paginator = Paginator(papers, 6)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        courses = Course.objects.all()
        semesters = Semester.objects.all()

        return render(request, 'papers/paper_list.html', {
            'page_obj': page_obj,
            'courses': courses,
            'semesters': semesters,
            'selected_course': course_id,
            'selected_exam_type': exam_type,
            'selected_semester': semester_id,
            'search_query': search_query or '',
            'upvoted_paper_ids': upvoted_paper_ids,
            'exam_choices': PastPaper.EXAM_CHOICES
        })


class PaperUploadView(View):
    """
    Open to all students (no login required!). Submissions require admin approval.
    """
    def get(self, request):
        form = PastPaperUploadForm()
        return render(request, 'papers/paper_upload.html', {'form': form})

    def post(self, request):
        form = PastPaperUploadForm(request.POST, request.FILES)
        if form.is_valid():
            paper = form.save(commit=False)
            
            if request.user.is_authenticated:
                paper.uploader = request.user
            else:
                paper.uploader = None
            
            # If user is staff/superuser, auto approve immediately
            if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
                paper.is_approved = True
                paper.approved_by = request.user
                paper.approved_at = timezone.now()
                paper.save()
                messages.success(request, f"Past Paper for '{paper.course.code}' uploaded and published directly as Administrator!")
            else:
                paper.is_approved = False
                paper.save()
                messages.success(request, f"Past Paper for '{paper.course.code}' uploaded successfully! It has been submitted to the admin approval queue.")
            
            return redirect('papers:paper_list')
        return render(request, 'papers/paper_upload.html', {'form': form})


class PaperDownloadView(View):
    """
    Allows download of approved past papers without requiring login.
    """
    def get(self, request, pk):
        paper = get_object_or_404(PastPaper, pk=pk)
        
        # Only allow download if approved OR if user is uploader/staff
        if not paper.is_approved and not (request.user.is_authenticated and (request.user.is_staff or paper.uploader == request.user)):
            messages.error(request, "This paper is currently pending admin approval.")
            return redirect('papers:paper_list')

        paper.download_count += 1
        paper.save(update_fields=['download_count'])

        file_path = paper.file.path
        if os.path.exists(file_path):
            filename = f"{paper.course.code}_{paper.exam_type}_{paper.year}.pdf"
            return FileResponse(open(file_path, 'rb'), content_type='application/pdf', as_attachment=True, filename=filename)
        else:
            raise Http404("File not found on server.")


@method_decorator(login_required, name='dispatch')
class PaperUpvoteView(View):
    def post(self, request, pk):
        paper = get_object_or_404(PastPaper, pk=pk)
        rating, created = PaperRating.objects.get_or_create(paper=paper, student=request.user)
        
        if not created:
            rating.delete()
            upvoted = False
            msg = "Upvote removed."
        else:
            upvoted = True
            msg = "Paper upvoted!"

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'upvoted': upvoted,
                'total_upvotes': paper.upvotes_count(),
                'message': msg
            })
            
        messages.success(request, msg)
        return redirect(request.META.get('HTTP_REFERER', 'papers:paper_list'))


@method_decorator(login_required, name='dispatch')
class PendingPapersQueueView(View):
    """
    Approval queue accessible by Staff/Admins & Student Admins.
    """
    def get(self, request):
        if not request.user.is_staff and not request.user.is_superuser:
            messages.error(request, "Access restricted. Only department administrators can access the approval queue.")
            return redirect('papers:dashboard')

        pending_papers = PastPaper.objects.filter(is_approved=False).select_related('course', 'semester', 'uploader')
        pending_seniors = StudentProfile.objects.filter(role='senior', is_approved=False).select_related('user')
        pending_posts = SeniorPost.objects.filter(is_approved=False).select_related('senior')

        return render(request, 'papers/pending_queue.html', {
            'pending_papers': pending_papers,
            'pending_seniors': pending_seniors,
            'pending_posts': pending_posts,
        })


@method_decorator(login_required, name='dispatch')
class ProcessPaperApprovalView(View):
    def post(self, request, pk, action):
        if not request.user.is_staff and not request.user.is_superuser:
            return HttpResponseForbidden("Permission denied.")
            
        paper = get_object_or_404(PastPaper, pk=pk)
        
        if action == 'approve':
            paper.is_approved = True
            paper.approved_by = request.user
            paper.approved_at = timezone.now()
            paper.save()
            messages.success(request, f"Paper '{paper.course.code}' approved and published to student portal.")
        elif action == 'reject':
            paper.delete()
            messages.info(request, "Pending paper submission rejected and removed.")
            
        return redirect('papers:pending_queue')


def custom_404_view(request, exception):
    return render(request, '404.html', status=404)

def custom_500_view(request):
    return render(request, '500.html', status=500)
