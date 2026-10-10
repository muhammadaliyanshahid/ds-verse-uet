from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib import messages
from apps.accounts.forms import StudentSignUpForm, ProfileEditForm
from apps.accounts.models import StudentProfile

class StudentSignUpView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('papers:dashboard')
        form = StudentSignUpForm()
        return render(request, 'accounts/signup.html', {'form': form})

    def post(self, request):
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to UET Data Science Portal, {user.first_name}! Your student profile has been created successfully.")
            return redirect('papers:dashboard')
        return render(request, 'accounts/signup.html', {'form': form})


class StudentLoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('papers:dashboard')
        form = AuthenticationForm()
        return render(request, 'accounts/login.html', {'form': form})

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('papers:dashboard')
        messages.error(request, "Invalid username or password. Please check your credentials.")
        return render(request, 'accounts/login.html', {'form': form})


class StudentLogoutView(View):
    def get(self, request):
        logout(request)
        messages.info(request, "You have been logged out safely.")
        return redirect('papers:landing')

    def post(self, request):
        logout(request)
        messages.info(request, "You have been logged out safely.")
        return redirect('papers:landing')


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        profile, created = StudentProfile.objects.get_or_create(user=request.user)
        form = ProfileEditForm(instance=profile, user=request.user)
        uploaded_papers = request.user.uploaded_papers.all()
        return render(request, 'accounts/profile.html', {
            'form': form,
            'profile': profile,
            'uploaded_papers': uploaded_papers
        })

    def post(self, request):
        profile, created = StudentProfile.objects.get_or_create(user=request.user)
        form = ProfileEditForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            profile = form.save(commit=False)
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            profile.save()
            messages.success(request, "Your profile details have been updated successfully.")
            return redirect('accounts:profile')
        uploaded_papers = request.user.uploaded_papers.all()
        return render(request, 'accounts/profile.html', {
            'form': form,
            'profile': profile,
            'uploaded_papers': uploaded_papers
        })
