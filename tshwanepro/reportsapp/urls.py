from django.urls import path
from . import views

app_name = 'reportsapp'

urlpatterns = [
    # Home page
    path('', views.home, name='home'),
    
    # Report form for each category
    path('report/<str:category>/', views.report_form, name='report_form'),
    
    # Confirmation page
    path('confirm/<str:tracking_id>/', views.confirm, name='confirm'),
    
    # Language switching
    path('language/<str:language>/', views.set_language, name='set_language'),
    
    # Simplified mode toggle
    path('toggle-simplified/', views.toggle_simplified_mode, name='toggle_simplified'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('secret-admin-login/', views.secret_admin_login, name='secret_admin_login'),
    
    # Admin Reports Management
    path('admin/reports/', views.admin_reports_list, name='admin_reports_list'),
    path('admin/reports/<str:tracking_id>/', views.admin_report_detail, name='admin_report_detail'),
]
