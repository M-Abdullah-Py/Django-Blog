# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.core.exceptions import ValidationError


class UserRegistrationForm(UserCreationForm):
    name = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}))
    bio = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Bio'}), required=False)
    image = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'}))

    class Meta:
        model = User
        fields = ('username', 'name', 'bio', 'image', 'password1', 'password2')


class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']



from django import forms
from .models import BlogPost
class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'image', 'description', 'content', 'sections', 'status', 'Category']  # exclude 'author'





class UserProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', "email" ,'bio', 'image']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Tell us about yourself...'}),
        }

        def clean_email(self):
            email = self.cleaned_data.get('email')

        # Check if the email already exists for another user
            if User.objects.filter(email=email).exclude(id=self.instance.id).exists():
                raise ValidationError('This email address is already in use. Please choose a different one.')

            return email
