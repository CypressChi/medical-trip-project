from django.contrib import admin
from django import forms
from .models import UserProfile, ChinaDoctor, Consultation, DoctorAvailability, DoctorReview


class DoctorAvailabilityForm(forms.ModelForm):
    """Custom form to allow hour-only input like '17' for time fields."""

    class Meta:
        model = DoctorAvailability
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        input_formats = ['%H:%M', '%H:%M:%S', '%H']
        self.fields['start_time'].input_formats = input_formats
        self.fields['end_time'].input_formats = input_formats


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
            'fields': ('user_profile', 'doctor', 'symptoms_description', 'report_file')
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


@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    """Admin interface for DoctorAvailability model."""
    form = DoctorAvailabilityForm
    list_display = ['doctor', 'date', 'start_time', 'end_time', 'created_at']
    list_filter = ['doctor', 'date']
    search_fields = ['doctor__name', 'doctor__hospital']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(DoctorReview)
class DoctorReviewAdmin(admin.ModelAdmin):
    """Admin interface for DoctorReview model."""
    list_display = ['consultation', 'stars', 'created_at']
    search_fields = ['consultation__id', 'consultation__doctor__name']
    readonly_fields = ['created_at', 'updated_at']
