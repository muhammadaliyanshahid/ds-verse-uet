from django.urls import path
from apps.papers import views

app_name = 'papers'

urlpatterns = [
    path('', views.LandingPageView.as_view(), name='landing'),
    path('gpa/', views.GpaCalculatorView.as_view(), name='gpa_calculator'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('papers/', views.PaperListView.as_view(), name='paper_list'),
    path('papers/upload/', views.PaperUploadView.as_view(), name='paper_upload'),
    path('papers/<int:pk>/download/', views.PaperDownloadView.as_view(), name='paper_download'),
    path('papers/<int:pk>/upvote/', views.PaperUpvoteView.as_view(), name='paper_upvote'),
    path('admin-queue/', views.PendingPapersQueueView.as_view(), name='pending_queue'),
    path('admin-queue/<int:pk>/<str:action>/', views.ProcessPaperApprovalView.as_view(), name='process_paper'),
]
