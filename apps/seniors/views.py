from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import HttpResponseForbidden

from apps.accounts.models import StudentProfile
from apps.seniors.models import SeniorPost, SeniorQuery
from apps.seniors.forms import SeniorSignUpForm, SeniorPostForm, SeniorQueryForm, SeniorReplyForm

class SeniorHubView(View):
    """
    Public Senior Guidance Hub: Browse Senior Mentors, read approved advice posts, and ask queries.
    """
    def get(self, request):
        approved_seniors = StudentProfile.objects.filter(role='senior', is_approved=True).select_related('user')
        
        category_filter = request.GET.get('category')
        posts = SeniorPost.objects.filter(is_approved=True).select_related('senior')
        if category_filter:
            posts = posts.filter(category=category_filter)

        query_form = SeniorQueryForm()
        if request.user.is_authenticated:
            query_form.fields['sender_name'].initial = request.user.get_full_name() or request.user.username
            query_form.fields['sender_email'].initial = request.user.email

        # Answered queries preview
        answered_queries = SeniorQuery.objects.filter(is_answered=True).select_related('target_senior')[:5]

        return render(request, 'seniors/hub.html', {
            'approved_seniors': approved_seniors,
            'posts': posts,
            'selected_category': category_filter,
            'categories': SeniorPost.CATEGORY_CHOICES,
            'query_form': query_form,
            'answered_queries': answered_queries,
        })


class SeniorSignUpView(View):
    """
    Allows Seniors / Alumni to register as mentors. Account requires Admin Approval.
    """
    def get(self, request):
        if request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.role == 'senior':
            messages.info(request, "You are already registered as a Senior Mentor.")
            return redirect('seniors:hub')
        form = SeniorSignUpForm()
        return render(request, 'seniors/signup.html', {'form': form})

    def post(self, request):
        form = SeniorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f"Senior Registration submitted for {user.get_full_name() or user.username}! "
                f"Your account is pending admin approval. You will be able to post and answer queries once approved."
            )
            return redirect('seniors:hub')
        return render(request, 'seniors/signup.html', {'form': form})


class SeniorQuerySubmitView(View):
    """
    Open view for ANY student or visitor (with or without account) to ask senior mentors questions.
    """
    def post(self, request):
        form = SeniorQueryForm(request.POST)
        if form.is_valid():
            query = form.save(commit=False)
            if request.user.is_authenticated:
                query.sender_user = request.user
            query.save()
            messages.success(request, "Your query has been submitted to Senior Mentors successfully! Check back in the Guidance Hub for answers.")
            return redirect('seniors:hub')
        
        messages.error(request, "There was an error in your query submission. Please fill in required fields.")
        return redirect('seniors:hub')


@method_decorator(login_required, name='dispatch')
class SeniorPostCreateView(View):
    """
    Allows approved Senior Mentors or Admins to submit guidance posts (requires Admin approval).
    """
    def get(self, request):
        profile = getattr(request.user, 'profile', None)
        if not (request.user.is_staff or (profile and profile.role == 'senior' and profile.is_approved)):
            messages.error(request, "Only approved Senior Mentors can write posts. If you just registered, your account is pending admin approval.")
            return redirect('seniors:hub')
            
        form = SeniorPostForm()
        return render(request, 'seniors/create_post.html', {'form': form})

    def post(self, request):
        profile = getattr(request.user, 'profile', None)
        if not (request.user.is_staff or (profile and profile.role == 'senior' and profile.is_approved)):
            return HttpResponseForbidden("Permission denied.")

        form = SeniorPostForm(request.POST)
        if form.is_valid():
            post_obj = form.save(commit=False)
            post_obj.senior = request.user
            
            # If staff/admin writes post, auto approve
            if request.user.is_staff or request.user.is_superuser:
                post_obj.is_approved = True
                post_obj.approved_by = request.user
                post_obj.approved_at = timezone.now()
                post_obj.save()
                messages.success(request, "Guidance post published directly as Administrator!")
            else:
                post_obj.is_approved = False
                post_obj.save()
                messages.success(request, "Guidance post submitted successfully! It has been sent to the Admin Approval Queue.")
            
            return redirect('seniors:hub')
        return render(request, 'seniors/create_post.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class SeniorDashboardView(View):
    """
    Dashboard for Senior Mentors to view received queries, answer questions, and manage posts.
    """
    def get(self, request):
        profile = getattr(request.user, 'profile', None)
        if not (request.user.is_staff or (profile and profile.role == 'senior')):
            messages.error(request, "Access restricted to Senior Mentors.")
            return redirect('seniors:hub')

        # Queries targeted to this senior OR open queries
        queries = SeniorQuery.objects.filter(target_senior=request.user) | SeniorQuery.objects.filter(target_senior__isnull=True)
        my_posts = request.user.senior_posts.all()

        return render(request, 'seniors/dashboard.html', {
            'profile': profile,
            'queries': queries.distinct(),
            'my_posts': my_posts,
        })

    def post(self, request):
        query_id = request.POST.get('query_id')
        reply_text = request.POST.get('reply')
        
        if query_id and reply_text:
            query = get_object_or_404(SeniorQuery, pk=query_id)
            query.reply = reply_text
            query.replied_at = timezone.now()
            query.is_answered = True
            query.save()
            messages.success(request, f"Reply submitted for query: '{query.subject}'!")
            
        return redirect('seniors:dashboard')


@method_decorator(login_required, name='dispatch')
class ProcessSeniorApprovalView(View):
    """
    Admin action to approve/reject pending senior accounts and pending senior posts.
    """
    def post(self, request, target_type, pk, action):
        if not request.user.is_staff and not request.user.is_superuser:
            return HttpResponseForbidden("Permission denied.")

        if target_type == 'mentor':
            profile = get_object_or_404(StudentProfile, pk=pk)
            if action == 'approve':
                profile.is_approved = True
                profile.save()
                messages.success(request, f"Senior Mentor account for '{profile.user.get_full_name() or profile.user.username}' approved!")
            elif action == 'reject':
                u = profile.user
                profile.delete()
                u.delete()
                messages.info(request, "Senior Mentor registration rejected and deleted.")

        elif target_type == 'post':
            post_obj = get_object_or_404(SeniorPost, pk=pk)
            if action == 'approve':
                post_obj.is_approved = True
                post_obj.approved_by = request.user
                post_obj.approved_at = timezone.now()
                post_obj.save()
                messages.success(request, f"Senior Post '{post_obj.title}' approved and published!")
            elif action == 'reject':
                post_obj.delete()
                messages.info(request, "Senior Post rejected and removed.")

        return redirect('papers:pending_queue')
