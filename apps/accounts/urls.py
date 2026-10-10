from django.urls import path
from apps.accounts import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.StudentSignUpView.as_view(), name='signup'),
    path('login/', views.StudentLoginView.as_view(), name='login'),
    path('logout/', views.StudentLogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
]
