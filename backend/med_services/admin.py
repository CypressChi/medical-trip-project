from django.contrib import admin
from django import forms
from .models import UserProfile, ChinaDoctor, Consultation


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin interface for UserProfile model.
    Displays username and North American phone number.
    """
    list_display = ['username', 'phone', 'language_preference', 'created_at']
    list_display_links = ['username']
    list_filter = ['language_preference', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    
    def username(self, obj):
        """Display the username from the related User model."""
        return obj.user.username
    
    username.short_description = "Username"


@admin.register(ChinaDoctor)
class ChinaDoctorAdmin(admin.ModelAdmin):
    """Admin interface for ChinaDoctor model."""
    list_display = ['name', 'hospital', 'department', 'years_of_experience', 'is_available']
    list_display_links = ['name']  # Make name clickable
    list_filter = ['department', 'is_available', 'hospital']
    search_fields = ['name', 'hospital', 'biography_en']  # searchable by name/hospital
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    """
    Admin interface for Consultation model.
    Displays patient, doctor, status, and creation date.
    AI suggestion is read-only in list view but editable in detail view.
    """
    list_display = ['id', 'patient', 'doctor', 'status', 'created_at']
    list_display_links = ['id', 'patient']
    list_filter = ['status']  # Filter by status (Pending/Confirmed/Completed)
    search_fields = ['user_profile__user__username', 'doctor__name', 'symptoms_description']
    list_select_related = ['user_profile__user', 'doctor']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    list_per_page = 25
    
    # Fieldset layout - ai_suggestion is editable here (not in readonly_fields)
    fieldsets = (
        ('Consultation Details', {
            'fields': ('user_profile', 'doctor', 'symptoms_description')
        }),
        ('AI Analysis', {
            'fields': ('ai_suggestion',),
            'description': 'AI-generated triage analysis (editable in detail view)'
        }),
        ('Status & Scheduling', {
            'fields': ('status', 'scheduled_at', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def patient(self, obj):
        """Display the patient name from UserProfile."""
        user = obj.user_profile.user
        full_name = user.get_full_name()
        return full_name if full_name else user.username
    
    def doctor(self, obj):
        """Display the doctor name."""
        return obj.doctor.name
    
    patient.short_description = "Patient"
    doctor.short_description = "Doctor"
