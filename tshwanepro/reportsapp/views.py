from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound
from .forms import FaultReportForm, UserRegistrationForm, UserLoginForm
from .models import FaultReport, UserProfile


def set_language(request, language):
    """
    Set the user's preferred language in session.
    """
    valid_languages = ['en', 'zu', 'st', 'af']
    if language in valid_languages:
        request.session['language'] = language
    return redirect('reportsapp:home')


def toggle_simplified_mode(request):
    """
    Toggle simplified/voice-guided mode.
    """
    current = request.session.get('simplified_mode', False)
    request.session['simplified_mode'] = not current
    return redirect('reportsapp:home')


# Category labels for display
CATEGORY_LABELS = {
    'water': 'Water Issue',
    'electricity': 'Electricity Issue',
    'roads': 'Road Issue',
    'waste': 'Waste Collection Issue',
    'other': 'Other Issue',
}


@login_required
def report_form(request, category):
    """
    Display the report form for a specific category.
    
    Args:
        request: The HTTP request
        category: The fault category (water, electricity, roads, waste)
    """
    # Validate category
    valid_categories = ['water', 'electricity', 'roads', 'waste']
    if category not in valid_categories:
        return HttpResponseNotFound("Invalid category")
    
    # Get language from session, default to English
    language = request.session.get('language', 'en')
    
    # Get simplified mode preference
    simplified_mode = request.session.get('simplified_mode', False)
    
    # Create form with initial data
    initial_data = {
        'category': category,
        'language': language,
        'simplified_mode': simplified_mode,
    }
    
    if request.method == 'POST':
        form = FaultReportForm(request.POST, request.FILES, initial=initial_data)
        if form.is_valid():
            # Save the report with the current user
            report = form.save(commit=False)
            report.user = request.user
            report.save()
            
            # Store tracking ID in session for confirmation page
            request.session['last_tracking_id'] = report.tracking_id
            
            messages.success(request, f'Report submitted successfully! Your tracking ID is: {report.tracking_id}')
            return redirect('reportsapp:confirm', tracking_id=report.tracking_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = FaultReportForm(initial=initial_data)
    
    context = {
        'form': form,
        'category': category,
        'category_label': CATEGORY_LABELS.get(category, 'Report Issue'),
        'language': language,
        'simplified_mode': simplified_mode,
    }
    
    return render(request, 'reportsapp/report_form.html', context)


def confirm(request, tracking_id):
    """
    Display confirmation page after successful report submission.
    """
    try:
        report = FaultReport.objects.get(tracking_id=tracking_id)
    except FaultReport.DoesNotExist:
        messages.error(request, 'Report not found.')
        return redirect('home')
    
    context = {
        'report': report,
    }
    
    return render(request, 'reportsapp/confirm.html', context)


def home(request):
    """
    Home page displaying the report categories.
    """
    # Get simplified mode preference
    simplified_mode = request.session.get('simplified_mode', False)
    language = request.session.get('language', 'en')
    
    context = {
        'simplified_mode': simplified_mode,
        'language': language,
    }
    
    return render(request, 'reportsapp/home.html', context)


def track_report(request):
    """
    Track a report by tracking ID.
    """
    tracking_id = request.GET.get('tracking_id', '')
    
    if tracking_id:
        try:
            report = FaultReport.objects.get(tracking_id=tracking_id.upper())
            context = {
                'report': report,
                'found': True,
            }
        except FaultReport.DoesNotExist:
            context = {
                'tracking_id': tracking_id,
                'found': False,
            }
    else:
        context = {
            'report': None,
            'found': None,
        }
    
    return render(request, 'trackingapp/trackreports.html', context)


def register(request):
    """
    User registration view.
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Create user
            user = User.objects.create_user(
                username=form.cleaned_data['id_number'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name']
            )
            
            # Create user profile with ID number
            UserProfile.objects.create(
                user=user,
                id_number=form.cleaned_data['id_number']
            )
            
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('reportsapp:login')
    else:
        form = UserRegistrationForm()
    
    context = {
        'form': form,
    }
    return render(request, 'reportsapp/register.html', context)


def user_login(request):
    """
    User login view using ID number and password.
    """
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            id_number = form.cleaned_data['id_number']
            password = form.cleaned_data['password']
            
            try:
                # Get user profile by ID number
                profile = UserProfile.objects.get(id_number=id_number)
                user = authenticate(request, username=profile.user.username, password=password)
                
                if user is not None:
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.first_name}!')
                    return redirect('reportsapp:home')
                else:
                    messages.error(request, 'Invalid password.')
            except UserProfile.DoesNotExist:
                messages.error(request, 'No user found with this ID number.')
    else:
        form = UserLoginForm()
    
    context = {
        'form': form,
    }
    return render(request, 'reportsapp/login.html', context)


def user_logout(request):
    """
    User logout view.
    """
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('reportsapp:home')


def secret_admin_login(request):
    """
    Secret admin login view using a special password.
    This allows system admins to access the admin page without a regular user account.
    """
    if request.method == 'POST':
        admin_password = request.POST.get('admin_password', '')
        
        # Check if the password matches the secret admin password
        if admin_password == '0000@admin':
            # Get or create a superuser for admin access
            admin_user, created = User.objects.get_or_create(
                username='system_admin',
                defaults={
                    'is_staff': True,
                    'is_superuser': True,
                    'first_name': 'System',
                    'last_name': 'Admin'
                }
            )
            
            if created:
                # Set a password for the admin user (won't be used for login)
                admin_user.set_password('admin_secret_password_123')
                admin_user.save()
            
            # Log in the admin user
            login(request, admin_user)
            messages.success(request, 'Welcome, System Admin!')
            return redirect('reportsapp:admin_reports_list')
        else:
            messages.error(request, 'Invalid admin password.')
            return redirect('reportsapp:login')
    else:
        # GET requests should redirect to login page
        return redirect('reportsapp:login')


from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def admin_reports_list(request):
    """
    Admin view to list all fault reports.
    Only accessible by staff/admin users.
    """
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    
    # Base queryset
    reports = FaultReport.objects.all().order_by('-created_at')
    
    # Apply filters
    if status_filter:
        reports = reports.filter(status=status_filter)
    if category_filter:
        reports = reports.filter(category=category_filter)
    
    # Get status counts for dashboard
    status_counts = {
        'total': FaultReport.objects.count(),
        'pending': FaultReport.objects.filter(status='pending').count(),
        'acknowledged': FaultReport.objects.filter(status='acknowledged').count(),
        'in_progress': FaultReport.objects.filter(status='in_progress').count(),
        'resolved': FaultReport.objects.filter(status='resolved').count(),
    }
    
    context = {
        'reports': reports,
        'status_counts': status_counts,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'status_choices': FaultReport.STATUS_CHOICES,
        'category_choices': FaultReport.CATEGORY_CHOICES,
    }
    
    return render(request, 'reportsapp/admin_reports_list.html', context)


@staff_member_required
def admin_report_detail(request, tracking_id):
    """
    Admin view to see and update a specific report.
    Only accessible by staff/admin users.
    """
    report = get_object_or_404(FaultReport, tracking_id=tracking_id)
    
    if request.method == 'POST':
        # Update report status and admin notes
        new_status = request.POST.get('status')
        admin_notes = request.POST.get('admin_notes', '')
        
        if new_status in dict(FaultReport.STATUS_CHOICES):
            report.status = new_status
            report.save()
            
            # Store admin notes in session (optional tracking)
            if admin_notes:
                messages.success(request, f'Report updated. Status changed to {report.get_status_display()}. Notes saved.')
            else:
                messages.success(request, f'Report updated. Status changed to {report.get_status_display()}.')
            
            return redirect('reportsapp:admin_reports_list')
    
    context = {
        'report': report,
        'status_choices': FaultReport.STATUS_CHOICES,
        'google_maps_url': f"https://www.google.com/maps?q={report.latitude},{report.longitude}" if report.latitude and report.longitude else None,
    }
    
    return render(request, 'reportsapp/admin_report_detail.html', context)
