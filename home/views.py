import datetime

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash, get_user_model
from django.contrib.auth.models import Permission
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import resolve, reverse, reverse_lazy
from django.views.generic import TemplateView, ListView

from django.utils import timezone

from nepali.datetime import NepaliDate

from dashboard.documents import NoticeDocument
from dashboard.models import Notice, Ministry, Office
from dashboard.mixins import ListSearchMixin, CustomLoginRequiredMixin, BaseMixin, NonDeletedListMixin

from .forms import FilterForm
from .models import BackgroundImage


# Create your views here.
class HomeView(NonDeletedListMixin, ListView):
    template_name = 'home/index.html'
    model = Notice
    paginate_by = 25
    search_fields = ['title__icontains', 'description__icontains']
    
    def get_queryset(self):
        queryset = super().get_queryset()

        form = FilterForm(data=self.request.GET)

        is_searched = False
        if form.is_valid():
            if form.is_filtered():
                # django elastic search get all existing notices
                search_result = NoticeDocument.search().extra(size=10000)
                print(search_result.to_queryset(), 4444444444444444)
                if self.request.GET.get('search') and (self.request.GET.get('search')!=None or self.request.GET.get('search')!=''):
                    search_result = search_result.query('multi_match', query=form.cleaned_data['search'], )
                    print(self.request.GET.get('search'))
                    print(search_result.to_queryset(), 22222222222222)
                    is_searched = True
                if self.request.GET.get('start_date') and (self.request.GET.get('start_date')!=None or self.request.GET.get('start_date')!=''):
                    start_date = form.cleaned_data['start_date']
                    search_result = search_result.query('range', **{'notice_date': {'gte': start_date} })

                if self.request.GET.get('end_date') and (self.request.GET.get('end_date')!=None or self.request.GET.get('end_date')!=''):
                    end_date = form.cleaned_data['end_date']
                    search_result = search_result.query('range', **{'notice_date': {'lte': end_date} })

                if self.request.GET.get('ministry'):
                    search_result = search_result.query('match', ministry=form.cleaned_data['ministry'].pk)

                # if self.request.GET.get('office'):
                #     search_result = search_result.query('match', office=form.cleaned_data['office'].pk)

                queryset = search_result.to_queryset() #convert search result to queryset and assign to queryset
            
        if not is_searched:
            queryset = queryset.order_by('-notice_date', '-id')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ministries"] = Ministry.objects.filter(deleted_at__isnull=True)
        context['offices'] = Office.objects.filter(deleted_at__isnull=True)
        context['background_image'] = BackgroundImage.get_instance()
        return context
