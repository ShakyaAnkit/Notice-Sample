from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth.forms import PasswordResetForm
from django.utils.html import mark_safe

from .models import Account, Category, User, Ministry, Office, Notice


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder':  'Username'}))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder':  'Password'}))

    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        user = User.objects.filter(username=username, is_active=True).first()
        if user == None or not user.check_password(password):
            raise forms.ValidationError("Incorrect username or password")
        return self.cleaned_data

class PasswordResetForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder':  'Current Password'}))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder':  'Password'}))
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder':  'Confirm Password'}))

    def set_user(self, user):
        self.user = user
    
    def clean(self):
        current_password = self.cleaned_data.get('current_password')
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')

        user = self.user
        if not user.check_password(current_password):
            raise forms.ValidationError({"current_password": "Incorrect password" })
        if not confirm_password:
            raise forms.ValidationError({'corfirm_password': "You must confirm your password" })
        if password != confirm_password:
            raise forms.ValidationError({'confirm_password': "Your passwords do not match" })

        return self.cleaned_data


class MinistryForm(forms.ModelForm):

    class Meta:
        model = Ministry
        fields = ['name',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })
    
    def clean(self):
        ministry = self.cleaned_data.get('name')

        if Ministry.objects.filter(name=ministry, deleted_at__isnull=True).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError({"name": "Ministry with this name already exists" })
        
        return self.cleaned_data

class OfficeForm(forms.ModelForm):

    class Meta:
        model = Office
        fields = ['ministry', 'name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

        self.fields['ministry'].widget.attrs.update({
                'class': 'form-control select2'
            })

        self.fields['ministry'].queryset = Ministry.objects.filter(deleted_at__isnull=True)

    def clean(self):
        ministry = self.cleaned_data.get('ministry')
        office = self.cleaned_data.get('name')

        if Office.objects.filter(ministry=ministry, name=office, deleted_at__isnull=True).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError({"name": "Office with this name already exists" })
        
        return self.cleaned_data

class AccountForm(forms.ModelForm):

    class Meta:
        model = Account
        fields = ['username', 'email', 'ministry', 'api_url']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })
        
        self.fields['email'].required = True
        
        self.fields['ministry'].widget.attrs.update({
                'class': 'form-control select2'
            })
        
        # self.fields['office'].widget.attrs.update({
        #         'class': 'form-control select2'
        #     })

        self.fields['ministry'].queryset = Ministry.objects.filter(deleted_at__isnull=True)
        # self.fields['office'].queryset = Office.objects.filter(deleted_at__isnull=True)
    
    def clean_email(self):
        email =  self.cleaned_data.get('email')

        # if Account.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
        #     raise forms.ValidationError("User with this email address already exists")
        
        return email


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        exclude = ('deleted_at', 'account', 'sync_id', 'ministry', 'office')
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })
        
        self.fields['notice_date'].widget.attrs.update({
            'class': 'form-control datepicker'
        })

        
