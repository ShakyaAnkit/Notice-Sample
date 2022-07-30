from django.contrib.auth import authenticate, login, logout, update_session_auth_hash, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import DeleteView

from .utils import AUDIT_CHOICES, storeAuditTrail

User = get_user_model()

class NonDeletedListMixin:
	def get_queryset(self):
		return super().get_queryset().filter(deleted_at__isnull=True)

class GetDeleteMixin:
	def get(self, request, *args, **kwargs):
		if hasattr(self, 'success_message'):
			messages.success(self.request, self.success_message)
		return super().delete(request, *args, **kwargs)

class NonLoginRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated and User.objects.filter(username=self.request.user.username, is_active=True).exists():
            return redirect('dashboard:index')
        return super().dispatch(request, *args, **kwargs)

class SuperAdminRequiredMixin:
	def dispatch(self, request, *args, **kwargs):
		if self.request.user.is_superuser:
			return super().dispatch(request, *args, **kwargs)
		return self.handle_no_permission()

class NonSuperAdminRequiredMixin:
	def dispatch(self, request, *args, **kwargs):
		if not self.request.user.is_superuser:
			return super().dispatch(request, *args, **kwargs)
		return self.handle_no_permission()

class CustomLoginRequiredMixin(LoginRequiredMixin):
	login_url = reverse_lazy('dashboard:login')

	def dispatch(self,request,*args,**kwargs):
		if self.request.user.is_superuser or self.request.user.is_active:
			return super().dispatch(request, *args, **kwargs)
		return self.handle_no_permission()

class BaseMixin():
	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(*args, **kwargs)
		context['account'] = self.get_account()
		return context

	def get_account(self):
		if hasattr(self.request.user, 'account'):
			return self.request.user.account
		return None

class ListSearchMixin:
	def get_queryset(self):
		queryset = super().get_queryset()
		search = self.request.GET.get('search', '').strip()
		if hasattr(self, 'search_fields') and search != '':
			filter_query = Q(pk__lt=0)
			for field in self.search_fields:
				filter_query = filter_query | Q(**{ field: search })
			queryset = queryset.filter(filter_query)
		return queryset

class CreateAuditMixin:
	def form_valid(self, form):
		storeAuditTrail(None, form.save(), AUDIT_CHOICES['CREATE'], self.request)
		return super().form_valid(form)

class UpdateAuditMixin:
	def form_valid(self, form):
		storeAuditTrail(self.get_object(), form.save(), AUDIT_CHOICES['UPDATE'], self.request)
		return super().form_valid(form)

class DeleteAuditMixin:
	def delete(self, request, *args, **kwargs):
		storeAuditTrail(self.get_object(), self.get_object(), AUDIT_CHOICES['DELETE'], request)
		return super().delete(request, *args, **kwargs)