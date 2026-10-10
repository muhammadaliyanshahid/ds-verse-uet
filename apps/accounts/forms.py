from django import forms
from django.contrib.auth.models import User
from apps.accounts.models import StudentProfile
from apps.timetable.models import Section

class StudentSignUpForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Ali'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Raza'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'e.g. ali.raza@student.uet.edu.pk'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create strong password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}))

    # Student Profile fields
    roll_number = forms.CharField(max_length=30, required=True, help_text="Format: YYYY-DS-XX", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '2023-DS-45'}))
    section = forms.ModelChoiceField(queryset=Section.objects.all(), required=False, empty_label="Select Section", widget=forms.Select(attrs={'class': 'form-select'}))
    semester_number = forms.IntegerField(min_value=1, max_value=8, initial=1, widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 8}))
    batch_year = forms.IntegerField(initial=2023, widget=forms.NumberInput(attrs={'class': 'form-control'}))

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
                roll_number=self.cleaned_data['roll_number'],
                section=self.cleaned_data['section'],
                semester_number=self.cleaned_data['semester_number'],
                batch_year=self.cleaned_data['batch_year']
            )
        return user


class ProfileEditForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    roll_number = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    section = forms.ModelChoiceField(queryset=Section.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    semester_number = forms.IntegerField(min_value=1, max_value=8, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+92 300 1234567'}))
    bio = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Tell us about your Data Science interests...'}), required=False)

    class Meta:
        model = StudentProfile
        fields = ['roll_number', 'section', 'semester_number', 'phone_number', 'bio']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
