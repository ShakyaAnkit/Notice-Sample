import io
import requests
import tempfile

from datetime import timedelta

from django.conf import settings as conf_settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash, get_user_model
from django.core import files
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect, render, Http404, HttpResponse
from django.urls import resolve, reverse, reverse_lazy
from django.views import View
from django.views.generic import TemplateView, FormView, ListView, CreateView, UpdateView, DeleteView, DetailView

from django.utils.crypto import get_random_string


from io import BytesIO

from .forms import  AccountForm, CategoryForm, MinistryForm, OfficeForm, LoginForm, PasswordResetForm, NoticeForm
from .mixins import (
    BaseMixin, 
    CustomLoginRequiredMixin, 
    GetDeleteMixin, 
    NonDeletedListMixin, 
    NonLoginRequiredMixin, 
    SuperAdminRequiredMixin, 
    NonSuperAdminRequiredMixin, 
    CreateAuditMixin,
    UpdateAuditMixin,
    DeleteAuditMixin,
)
from .models import Account, Category, Ministry, Office, Notice, AuditTrail
from .utils import AUDIT_CHOICES, storeAuditTrail


# for future use
# from .utils import content_file_from_url 

User = get_user_model()

class DashboardView(CustomLoginRequiredMixin,  BaseMixin, TemplateView):
    template_name = 'dashboard/index.html'

        
# Git Pull View
class GitPullView(SuperAdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        import subprocess
        process = subprocess.Popen(['./pull.sh'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        returncode = process.wait()
        output = ''
        output += process.stdout.read().decode("utf-8")
        output += '\nReturned with status {0}'.format(returncode)
        response = HttpResponse(output)
        response['Content-Type'] = 'text'
        return response


# Login Logout Views
class LoginPageView(NonLoginRequiredMixin, FormView):
    form_class = LoginForm
    template_name = "dashboard/auth/login.html"

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)
        
        # Remember me
        if self.request.POST.get('remember', None) == None:
            self.request.session.set_expiry(0)
        
        login(self.request, user)

        storeAuditTrail(None, user, AUDIT_CHOICES['LOGIN'], self.request)
        if 'next' in self.request.GET:
            return redirect(self.request.GET.get('next'))
        if not self.request.user.is_superuser:
            return redirect('dashboard:notices-list')
        return redirect('dashboard:index')
        
class LogoutView(CustomLoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        storeAuditTrail(None, self.request.user, AUDIT_CHOICES['LOGOUT'], request)
        logout(request)
        return redirect('dashboard:login')
    

# Password Reset
class ChangePasswordView(CustomLoginRequiredMixin, SuccessMessageMixin, FormView):
    form_class = PasswordResetForm
    template_name = "dashboard/auth/change_password.html"
    success_message = "Password Has Been Changed"
    success_url = reverse_lazy('dashboard:index')

    def get_form(self):
        form = super().get_form()
        form.set_user(self.request.user)
        return form

    def form_valid(self, form):
        password = form.cleaned_data['confirm_password']
        account = User.objects.filter(username=self.request.user).first()
        account.set_password(form.cleaned_data['confirm_password'])
        account.save(update_fields=['password'])
        user = authenticate(username=self.request.user, password=password)
        login(self.request, user)
        return super().form_valid(form)


# Ministry CRUD
class MinistryListView(CustomLoginRequiredMixin, SuperAdminRequiredMixin, NonDeletedListMixin, ListView):
    model = Ministry
    template_name = "dashboard/ministries/list.html"
    paginate_by = 100

    def get_queryset(self):
        return super().get_queryset().order_by('-created_at')

class MinistryCreateView(CustomLoginRequiredMixin, SuperAdminRequiredMixin, SuccessMessageMixin, CreateAuditMixin, CreateView):
    form_class = MinistryForm
    success_message = "Ministry Created Successfully"
    success_url = reverse_lazy('dashboard:ministries-list')
    template_name = "dashboard/ministries/form.html"

class MinistryUpdateView(CustomLoginRequiredMixin, SuperAdminRequiredMixin, NonDeletedListMixin, SuccessMessageMixin, UpdateAuditMixin, UpdateView):
    form_class = MinistryForm
    model = Ministry
    success_message = "Ministry Updated Successfully"
    success_url = reverse_lazy('dashboard:ministries-list')
    template_name = "dashboard/ministries/form.html"

class MinistryDeleteView(CustomLoginRequiredMixin, SuperAdminRequiredMixin, NonDeletedListMixin, SuccessMessageMixin, GetDeleteMixin, DeleteAuditMixin, DeleteView):
    model = Ministry
    success_message = "Ministry Deleted Successfully"
    success_url = reverse_lazy('dashboard:ministries-list')


# Office CRUD
# class OfficeListView(CustomLoginRequiredMixin, SuperAdminRequiredMixin, NonDeletedListMixin, ListView):
#     model = Office
#     template_name = "dashboard/offices/list.html"
#     paginate_by = 100

#     def get_queryset(self):
#         return super().get_queryset().order_by('-created_at')

# class OfficeCreateView(CustomLoginRequiredMixin, SuperAdminRequiredMixin, SuccessMessageMixin, CreateAuditMixin, CreateView):
#     form_class= OfficeForm
#     success_message = "Office Created Successfully"
#     success_url = reverse_lazy('dashboard:offices-list')
#     template_name = "dashboard/offices/form.html"

# class OfficeUpdateView(CustomLoginRequiredMixin, SuperAdminRequiredMixin, NonDeletedListMixin, SuccessMessageMixin, UpdateAuditMixin, UpdateView):
#     form_class = OfficeForm
#     model = Office
#     success_message = "Office Updated Successfully"
#     success_url = reverse_lazy('dashboard:offices-list')
#     template_name = "dashboard/offices/form.html"

# class OfficeDeleteView(CustomLoginRequiredMixin, SuperAdminRequiredMixin, NonDeletedListMixin, SuccessMessageMixin, GetDeleteMixin, DeleteAuditMixin, DeleteView):
#     model = Office
#     success_message = "Office Deleted Successfully"
#     success_url = reverse_lazy('dashboard:offices-list')


# Ajax Call for Office
# class OfficeAjaxView(ListView):
#     model = Office
#     template_name = "dashboard/dropdowns/office_list.html"

#     def get(self, request, *args, **kwargs):
#         ministry_id = self.request.GET.get('ministry_id')
#         if ministry_id:
#             offices = Office.objects.filter(ministry=ministry_id, deleted_at__isnull=True)
#         else:
#             offices = Office.objects.filter(deleted_at__isnull=True)
#         return render(request, self.template_name, {'offices' : offices })



# Account CRUD
class AccountListView(CustomLoginRequiredMixin, SuperAdminRequiredMixin, ListView):
    model = Account
    template_name = "dashboard/accounts/list.html"
    paginate_by = 100

class AccountCreateView(CustomLoginRequiredMixin, SuperAdminRequiredMixin, SuccessMessageMixin, CreateAuditMixin, CreateView):
    form_class= AccountForm
    success_message = "Account Created Successfully"
    template_name = "dashboard/accounts/form.html"

    def get_success_url(self):
        return reverse('dashboard:password-reset', kwargs={'pk': self.object.pk })
    

class AccountUpdateView(CustomLoginRequiredMixin, SuperAdminRequiredMixin, SuccessMessageMixin, UpdateAuditMixin, UpdateView):
    form_class = AccountForm
    model = Account
    success_message = "Account Updated Successfully"
    success_url = reverse_lazy('dashboard:accounts-list')
    template_name = "dashboard/accounts/form.html"


class AccountStatusView(CustomLoginRequiredMixin, SuperAdminRequiredMixin, SuccessMessageMixin, View):
    model = Account
    success_message = "User's Status Has Been Changed Successfully"
    success_url = reverse_lazy('dashboard:accounts-list')

    def get(self, request, *args, **kwargs):
        user_id = self.kwargs['pk']
        if user_id:
            account = Account.objects.filter(pk=user_id).first()
            if account.is_active == True:
                account.is_active = False
            else:
                account.is_active = True
            account.save(update_fields=['is_active'])
        return redirect(self.success_url)


# Password Reset
class PasswordResetView(CustomLoginRequiredMixin, SuccessMessageMixin, View):
    model = Account
    success_url = reverse_lazy("dashboard:accounts-list")
    success_message = "Password has been sent to the user's email."

    def get(self, request, *args, **kwargs):
        user_pk = self.kwargs["pk"]
        account = Account.objects.filter(pk=user_pk).first()
        password = get_random_string(length=6)
        account.set_password(password)
        msg = (
            "You can login to Suchana Portal with the following credentials.\n\n" + "Username: " + account.username + " \n" + "Password: " + password
        )
        send_mail("Suchana Portal password has been changed", msg, conf_settings.EMAIL_HOST_USER, [account.email], fail_silently=True)
        account.save(update_fields=["password"])

        messages.success(self.request, self.success_message)
        return redirect(self.success_url)

# Categories CRUD
class CategoryListView(CustomLoginRequiredMixin, SuperAdminRequiredMixin, NonDeletedListMixin, ListView):
    model = Category
    template_name = "dashboard/categories/list.html"
    paginate_by = 100

    def get_queryset(self):
        return super().get_queryset().order_by('-created_at')

class CategoryCreateView(CustomLoginRequiredMixin, SuperAdminRequiredMixin, SuccessMessageMixin, CreateAuditMixin, CreateView):
    form_class= CategoryForm
    success_message = "Category Created Successfully"
    success_url = reverse_lazy('dashboard:categories-list')
    template_name = "dashboard/categories/form.html"


class CategoryUpdateView(CustomLoginRequiredMixin, SuperAdminRequiredMixin, NonDeletedListMixin, SuccessMessageMixin, UpdateAuditMixin, UpdateView):
    form_class = CategoryForm
    model = Category
    success_message = "Category Updated Successfully"
    success_url = reverse_lazy('dashboard:categories-list')
    template_name = "dashboard/categories/form.html"


class CategoryDeleteView(CustomLoginRequiredMixin, SuperAdminRequiredMixin, NonDeletedListMixin, SuccessMessageMixin, GetDeleteMixin, DeleteAuditMixin, DeleteView):
    model = Category
    success_message = "Category Deleted Successfully"
    success_url = reverse_lazy('dashboard:categories-list')


# Notice CRUD
class NoticeQuerySetMixin(BaseMixin):
    def get_queryset(self):
        queryset = super().get_queryset() 
        account = self.get_account()
        queryset = self.model.objects.filter(deleted_at__isnull=True, ministry=account.ministry, office=account.office)
        return queryset

class NoticeListView(NoticeQuerySetMixin, BaseMixin, CustomLoginRequiredMixin, NonDeletedListMixin, NonSuperAdminRequiredMixin, ListView):
    model = Notice
    template_name = 'dashboard/notices/list.html'
    paginate_by = 100
    
class NoticeCreateView(BaseMixin, CustomLoginRequiredMixin, SuccessMessageMixin, NonSuperAdminRequiredMixin, CreateAuditMixin, CreateView):
    model = Notice
    template_name = "dashboard/notices/form.html"
    form_class = NoticeForm
    success_message = "Notice Created Successfully"
    success_url = reverse_lazy('dashboard:notices-list')

    def form_valid(self, form):
        account = self.get_account()
        form.instance.ministry = account.ministry
        form.instance.office = account.office
        form.instance.account = account
        return super().form_valid(form)

class NoticeDetailView(NoticeQuerySetMixin, CustomLoginRequiredMixin, NonDeletedListMixin, NonSuperAdminRequiredMixin, DetailView):
    model = Notice
    template_name = 'dashboard/notices/detail.html'

class NoticeUpdateView(NoticeQuerySetMixin, CustomLoginRequiredMixin, NonDeletedListMixin, SuccessMessageMixin, NonSuperAdminRequiredMixin, UpdateAuditMixin, UpdateView):
    template_name = "dashboard/notices/form.html"
    model = Notice
    form_class = NoticeForm
    success_url = reverse_lazy('dashboard:notices-list')
    success_message = "Notice updated Successfully"


class NoticeDeleteView(NoticeQuerySetMixin, CustomLoginRequiredMixin, NonDeletedListMixin, SuccessMessageMixin, NonSuperAdminRequiredMixin, GetDeleteMixin, DeleteAuditMixin, DeleteView):
    model = Notice
    success_message = "Notice  Deleted Successfully"
    success_url = reverse_lazy('dashboard:notices-list')

# Sync Notice 
class NoticeSyncApiView(BaseMixin, CustomLoginRequiredMixin, NonDeletedListMixin, NonSuperAdminRequiredMixin, View):
    model = Notice

    def get(self, request, *args, **kwargs):
        self.save_notices()
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('dashboard:notices-list')

    def get_notices_api(self):
        account = self.get_account()
        if account != None and account.api_url != None:
            try: 
                notices_api = requests.get(account.api_url).json()
            except:
                raise Http404
            return notices_api

        raise Http404

    def save_notices(self):
        account = self.get_account()
        notice_sync_id_list = list(self.model.objects.filter(deleted_at__isnull=True, ministry=account.ministry, office=account.office) .values_list('sync_id', flat=True))
        
        for notice in self.get_notices_api():
            if self.model.objects.filter(sync_id=notice['id'], ministry=account.ministry, office=account.office, deleted_at__isnull=True).exists():
                # Updating the notice if notices already exists
                notice_object = self.model.objects.filter(sync_id=notice['id'], account=account, deleted_at__isnull=True).first()
                notice_object.account = account
                notice_object.title = notice['title']
                notice_object.description = notice['description']
                notice_object.api_file_url = notice['document_file']
                notice_object.notice_date = notice['notice_date']
                # notice_object.office = account.office
                notice_object.ministry = account.ministry
                notice_object.link = account.api_url.split('/api')[0] + '/notice/{}'.format(notice['id'])
                
                # for future use

                # if notice['document_file'] != None:
                #     notice_object.document_file = content_file_from_url(notice['document_file'])

                notice_object.save(update_fields=['title', 'description', 'api_file_url', 'sync_id', 'notice_date', 'office'])
            else:
                # Create a new notices if notice doesnot exist
                notice_object = self.model(sync_id=notice['id'])
                notice_object.account = account
                notice_object.title = notice['title']
                notice_object.description = notice['description']
                # notice_object.office = account.office
                notice_object.ministry = account.ministry
                notice_object.api_file_url = notice['document_file']
                notice_object.notice_date = notice['notice_date']
                notice_object.link = account.api_url.split('/api')[0] + '/notice/{}'.format(notice['id'])

                # for future use
                
                # if notice['document_file'] != None:
                #     notice_object.document_file = content_file_from_url(notice['document_file'])
                
                notice_object.save()

            # remove sync_id if it exists 
            if notice['id'] in notice_sync_id_list:
                notice_sync_id_list.remove(notice['id'])

        # deleting notices from db
        self.model.objects.filter(deleted_at__isnull=True, ministry=account.ministry, office=account.office, sync_id__in=notice_sync_id_list).delete()


# Audit Trail
class AuditTrailList(SuperAdminRequiredMixin, ListView):
    template_name = 'dashboard/audit_trail/list.html'
    model = AuditTrail
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = AuditTrail.objects.all().order_by('-created_at')
        return queryset
    