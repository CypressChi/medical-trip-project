from django.contrib import admin
from django import forms
from .models import UserProfile, ChinaDoctor, Consultation


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for UserProfile model."""
    list_display = ['user', 'phone', 'language_preference', 'created_at']
    list_display_links = ['user']  # Make user clickable
    list_filter = ['language_preference', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ChinaDoctor)
class ChinaDoctorAdmin(admin.ModelAdmin):
    """Admin interface for ChinaDoctor model."""
    list_display = ['name', 'hospital', 'department', 'years_of_experience', 'is_available']
    list_display_links = ['name']  # Make name clickable
    list_filter = ['department', 'is_available', 'hospital']
    search_fields = ['name', 'hospital', 'biography_en']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    """Admin interface for Consultation model with improved datetime input."""
    list_display = ['id', 'user_profile', 'doctor', 'status', 'scheduled_at', 'created_at']
    list_display_links = ['id', 'user_profile']  # Make ID and user_profile clickable
    list_filter = ['status', 'created_at', 'scheduled_at']
    search_fields = ['user_profile__user__username', 'doctor__name', 'symptoms_description']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    list_per_page = 25  # Show 25 records per page
    
    # Improve fieldset layout and enable custom time input
    fieldsets = (
        ('Consultation Details', {
            'fields': ('user_profile', 'doctor', 'symptoms_description')
        }),
        ('AI Analysis', {
            'fields': ('ai_suggestion',),
            'classes': ('collapse',)
        }),
        ('Status & Scheduling', {
            'fields': ('status', 'scheduled_at', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
