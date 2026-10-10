from django.contrib import admin
from django.utils import timezone
from apps.seniors.models import SeniorPost, SeniorQuery

@admin.register(SeniorPost)
class SeniorPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'senior', 'category', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'category', 'created_at')
    search_fields = ('title', 'content', 'senior__username', 'senior__first_name', 'senior__last_name')
    actions = ['approve_selected_posts', 'reject_selected_posts']

    @admin.action(description="Approve selected senior posts for publishing")
    def approve_selected_posts(self, request, queryset):
        updated = queryset.update(
            is_approved=True,
            approved_by=request.user,
            approved_at=timezone.now()
        )
        self.message_user(request, f"Successfully approved {updated} senior post(s).")

    @admin.action(description="Reject selected senior posts")
    def reject_selected_posts(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"Successfully rejected {count} senior post(s).")


@admin.register(SeniorQuery)
class SeniorQueryAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sender_name', 'target_senior', 'is_answered', 'created_at')
    list_filter = ('is_answered', 'created_at')
    search_fields = ('subject', 'message', 'sender_name', 'sender_email')
