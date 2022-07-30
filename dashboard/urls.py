from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns=[       
        path('', views.DashboardView.as_view(), name='index'),

        # git-pull
        path('git-pull', views.GitPullView.as_view(), name='git-pull'),
        
        # accounts
        path('accounts/login/', views.LoginPageView.as_view(), name='login'),
        path('accounts/logout/', views.LogoutView.as_view(), name='logout'),
        path('accounts/change-password/', views.ChangePasswordView.as_view(), name='change-password'),

        # Ministry CRUD
        path('ministries/', views.MinistryListView.as_view(), name='ministries-list'),
        path('ministries/create', views.MinistryCreateView.as_view(), name='ministries-create'),
        path('ministries/<int:pk>/update', views.MinistryUpdateView.as_view(), name='ministries-update'),
        path('ministries/<int:pk>/delete', views.MinistryDeleteView.as_view(), name='ministries-delete'),

        # Office CRUD
        # path('offices/', views.OfficeListView.as_view(), name='offices-list'),
        # path('offices/create', views.OfficeCreateView.as_view(), name='offices-create'),
        # path('offices/<int:pk>/update', views.OfficeUpdateView.as_view(), name='offices-update'),
        # path('offices/<int:pk>/delete', views.OfficeDeleteView.as_view(), name='offices-delete'),
        # path('offices/ajax', views.OfficeAjaxView.as_view(), name='offices-ajax'),

        # Account CRUD
        path('users/', views.AccountListView.as_view(), name='accounts-list'),
        path('users/create', views.AccountCreateView.as_view(), name='accounts-create'),
        path('users/<int:pk>/update', views.AccountUpdateView.as_view(), name='accounts-update'),
        path('users/<int:pk>/status', views.AccountStatusView.as_view(), name='accounts-status'),

        # Password Reset
        path('users/<int:pk>/password-reset', views.PasswordResetView.as_view(), name='password-reset'),

        # Categories CRUD
        path('categories/', views.CategoryListView.as_view(), name='categories-list'),
        path('categories/create', views.CategoryCreateView.as_view(), name='categories-create'),
        path('categories/<int:pk>/update', views.CategoryUpdateView.as_view(), name='categories-update'),
        path('categories/<int:pk>/delete', views.CategoryDeleteView.as_view(), name='categories-delete'),
        
        #Notice CRUD
        path('notices/', views.NoticeListView.as_view(), name='notices-list'),
        path('notices/create', views.NoticeCreateView.as_view(), name='notices-create'),
        path('notices/<int:pk>/detail', views.NoticeDetailView.as_view(), name='notices-detail'),
        path('notices/<int:pk>/update', views.NoticeUpdateView.as_view(), name='notices-update'),
        path('notices/<int:pk>/delete', views.NoticeDeleteView.as_view(), name='notices-delete'),
        path('notices/sync-api', views.NoticeSyncApiView.as_view(), name='notices-sync-api'),

        # AuditTrail List
        path('audits/', views.AuditTrailList.as_view(), name="audittrail-list"),
]