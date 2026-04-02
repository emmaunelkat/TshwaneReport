from django.contrib import admin
from .models import FaultReport


@admin.register(FaultReport)
class FaultReportAdmin(admin.ModelAdmin):
    list_display = ('tracking_id', 'category', 'status', 'address', 'created_at')
    list_filter = ('category', 'status', 'language', 'created_at')
    search_fields = ('tracking_id', 'address', 'description')
    readonly_fields = ('tracking_id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Report Details', {
            'fields': ('tracking_id', 'category', 'description', 'photo')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude', 'address')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('User Preferences', {
            'fields': ('language', 'simplified_mode')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
