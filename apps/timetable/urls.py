from django.urls import path
from apps.timetable import views

app_name = 'timetable'

urlpatterns = [
    path('', views.TimetableView.as_view(), name='grid'),
]
