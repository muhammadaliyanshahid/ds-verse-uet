from django.contrib import admin
from apps.accounts.models import StudentProfile

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('roll_number', 'get_full_name', 'get_email', 'section', 'semester_number', 'batch_year', 'is_staff_status')
    list_filter = ('section', 'semester_number', 'batch_year', 'user__is_staff')
    search_fields = ('roll_number', 'user__username', 'user__first_name', 'user__last_name', 'user__email')
    ordering = ('roll_number',)

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_full_name.short_description = 'Student Name'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email Address'

    def is_staff_status(self, obj):
        return obj.user.is_staff
    is_staff_status.boolean = True
    is_staff_status.short_description = 'Admin / Staff'
