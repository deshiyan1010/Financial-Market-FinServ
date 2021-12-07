from django import forms
from reg_sign_in_out.models import *
from django.contrib.auth.models import User

class UserForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30,required=True,
                                widget = forms.TextInput(attrs={'class': 'input'}))
    last_name = forms.CharField(max_length=30,required=True,
                                widget = forms.TextInput(attrs={'class': 'input'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input'}),)
    
    username = forms.CharField(max_length=30,required=True,
                                widget = forms.TextInput(attrs={'class': 'input'}))
    email = forms.CharField(max_length=30,required=True,
                                widget = forms.TextInput(attrs={'class': 'input'}))
    class Meta:
        model = User
        fields = ('first_name','last_name','username','email','password',)

    def clean_username(self):
        username = self.cleaned_data['username']

        if User.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            raise forms.ValidationError('Exists')
        return username


class RegistrationForm(forms.ModelForm):
    
    class Meta:
        model = Registration
        fields = ('phone_number',)
