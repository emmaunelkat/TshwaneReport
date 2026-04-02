from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


class UserProfile(models.Model):
    """
    Extended user profile with additional fields for South African ID.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    id_number = models.CharField(
        max_length=13,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{13}$',
                message='ID number must be exactly 13 digits.'
            )
        ],
        help_text='South African ID number (13 digits)'
    )
    phone = models.CharField(max_length=15, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.id_number})"


class FaultReport(models.Model):
    """
    Model for reporting faults in Tshwane municipality.
    Categories: water, electricity, roads, waste
    """
    
    CATEGORY_CHOICES = [
        ('water', 'Water'),
        ('electricity', 'Electricity'),
        ('roads', 'Roads'),
        ('waste', 'Waste'),
        ('other', 'Other'),
    ]
    
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('zu', 'Zulu'),
        ('st', 'Sesotho'),
        ('af', 'Afrikaans'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('acknowledged', 'Acknowledged'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]
    
    # User who submitted the report
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports')
    
    # Report details
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to='reports/photos/', blank=True, null=True)
    
    # Location data (populated by GPS or manual entry)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    
    # Tracking info
    tracking_id = models.CharField(max_length=20, unique=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # User preferences
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='en')
    simplified_mode = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Fault Report'
        verbose_name_plural = 'Fault Reports'
    
    def __str__(self):
        return f"{self.get_category_display()} - {self.tracking_id} ({self.status})"
    
    def save(self, *args, **kwargs):
        if not self.tracking_id:
            import uuid
            self.tracking_id = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)
    
    @property
    def category_icon(self):
        """Return emoji icon based on category."""
        icons = {
            'water': '💧',
            'electricity': '⚡',
            'roads': '🚧',
            'waste': '🗑️',
            'other': '📋',
        }
        return icons.get(self.category, '📋')
    
    @property
    def reference_number(self):
        """Alias for tracking_id for template compatibility."""
        return self.tracking_id
    
    def get_status_badge_color(self):
        """Return CSS class suffix for status badge color."""
        colors = {
            'pending': 'warning',
            'acknowledged': 'info',
            'in_progress': 'primary',
            'resolved': 'success',
        }
        return colors.get(self.status, 'secondary')
