from django import forms
from django.contrib.auth.models import User
from apps.accounts.models import StudentProfile
from apps.seniors.models import SeniorPost, SeniorQuery

class SeniorSignUpForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Hassan'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Tariq'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'e.g. hassan.tariq@student.uet.edu.pk'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create strong password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}))

    roll_number = forms.CharField(max_length=30, required=True, help_text="e.g. 2021-DS-05", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '2021-DS-05'}))
    batch_year = forms.IntegerField(initial=2021, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2021'}))
    expertise = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Computer Vision, Machine Learning, FYPs'}), help_text="Areas you can mentor junior students in.")
    linkedin_url = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://linkedin.com/in/yourprofile'}))
    bio = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Share your experience, achievements, or current role...'}), required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose username'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with this email address already exists.")
        return email

    def clean_roll_number(self):
        roll = self.cleaned_data.get('roll_number')
        if StudentProfile.objects.filter(roll_number__iexact=roll).exists():
            raise forms.ValidationError("This roll number is already registered.")
        return roll

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            StudentProfile.objects.create(
                user=user,
                role='senior',
                roll_number=self.cleaned_data['roll_number'],
                semester_number=8,
                batch_year=self.cleaned_data['batch_year'],
                expertise=self.cleaned_data['expertise'],
                linkedin_url=self.cleaned_data.get('linkedin_url'),
                bio=self.cleaned_data.get('bio'),
                is_approved=False  # Requires Admin Approval!
            )
        return user


class SeniorPostForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Key Preparation Steps for ML & AI Internships'}))
    category = forms.ChoiceField(choices=SeniorPost.CATEGORY_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Share your valuable advice, study tips, or FYP guidance for juniors...'}))

    class Meta:
        model = SeniorPost
        fields = ['title', 'category', 'content']


class SeniorQueryForm(forms.ModelForm):
    target_senior = forms.ModelChoiceField(
        queryset=User.objects.filter(profile__role='senior', profile__is_approved=True),
        required=False,
        empty_label="All Senior Mentors",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    sender_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name or Roll Number'}))
    sender_email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Optional Email for reply notification'}))
    subject = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Help needed regarding Database Systems course / FYP Selection'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Explain your question, difficulty, or guidance needed...'}))

    class Meta:
        model = SeniorQuery
        fields = ['target_senior', 'sender_name', 'sender_email', 'subject', 'message']


class SeniorReplyForm(forms.ModelForm):
    reply = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Write your helpful answer / guidance for the student...'}))

    class Meta:
        model = SeniorQuery
        fields = ['reply']
