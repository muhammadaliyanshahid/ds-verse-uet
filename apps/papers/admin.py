from django.contrib import admin
from django.utils import timezone
from apps.papers.models import Course, PastPaper, PaperRating

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'semester_number', 'credit_hours')
    list_filter = ('semester_number', 'credit_hours')
    search_fields = ('code', 'title')
    ordering = ('semester_number', 'code')


@admin.register(PastPaper)
class PastPaperAdmin(admin.ModelAdmin):
    list_display = ('course', 'exam_type', 'year', 'semester', 'uploader', 'is_approved', 'approved_by', 'upload_date', 'download_count')
    list_filter = ('is_approved', 'exam_type', 'semester', 'year', 'course')
    search_fields = ('course__code', 'course__title', 'uploader__username', 'uploader__first_name', 'uploader__last_name')
    actions = ['approve_selected_papers', 'reject_selected_papers']

    @admin.action(description="Approve selected past papers for publishing")
    def approve_selected_papers(self, request, queryset):
        updated_count = queryset.update(
            is_approved=True,
            approved_by=request.user,
            approved_at=timezone.now()
        )
        self.message_user(request, f"Successfully approved {updated_count} past paper(s).")

    @admin.action(description="Reject selected past papers")
    def reject_selected_papers(self, request, queryset):
        deleted_count = queryset.count()
        queryset.delete()
        self.message_user(request, f"Successfully rejected and removed {deleted_count} past paper(s).")


@admin.register(PaperRating)
class PaperRatingAdmin(admin.ModelAdmin):
    list_display = ('paper', 'student', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('paper__course__code', 'student__username')
