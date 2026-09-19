from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import UserProfile
from django import forms
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3

class SendEmailForm(forms.Form):
    subject = forms.CharField(max_length=255, required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)
    captcha = ReCaptchaField(widget=ReCaptchaV3)

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['about_me']
        widgets = {
            'about_me': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Tell us about yourself...',
                'style': 'width: 100%; border-radius: 4px; border: 1px solid #ddd;'
            }),
        }

class SignUpForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-input', 'placeholder': 'First Name'
    }))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-input', 'placeholder': 'Last Name'
    }))
    username = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={
        'class': 'form-input', 'placeholder': 'Username'
    }))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-input', 'placeholder': 'Email Address'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input', 'placeholder': 'Password'
    }))
    captcha = ReCaptchaField(widget=ReCaptchaV3)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()

            # Use get_or_create so it works whether a signal exists or not
            profile, created = UserProfile.objects.get_or_create(user=user)

            is_under_13 = self.cleaned_data.get('under_13', False)
            profile.is_child = is_under_13
            profile.is_approved = not is_under_13

            if is_under_13 and self.cleaned_data.get('consent_png'):
                profile.consent_form = self.cleaned_data['consent_png']

            profile.save()

        return user


class EmailLoginForm(AuthenticationForm):
    """
    Standard login form tailored with custom CSS classes.
    Note: Django authentication checks 'username' and 'password'.
    If you want users to log in explicitly using their email instead of username,
    you'll want to configure an authentication backend.
    """
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-input', 'placeholder': 'Username or Email'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input', 'placeholder': 'Password'
    }))
    captcha = ReCaptchaField(widget=ReCaptchaV3)