from django.urls import path
from apps.seniors import views

app_name = 'seniors'

urlpatterns = [
    path('', views.SeniorHubView.as_view(), name='hub'),
    path('signup/', views.SeniorSignUpView.as_view(), name='signup'),
    path('post/new/', views.SeniorPostCreateView.as_view(), name='create_post'),
    path('query/ask/', views.SeniorQuerySubmitView.as_view(), name='submit_query'),
    path('dashboard/', views.SeniorDashboardView.as_view(), name='dashboard'),
    path('approval/<str:target_type>/<int:pk>/<str:action>/', views.ProcessSeniorApprovalView.as_view(), name='process_approval'),
]
