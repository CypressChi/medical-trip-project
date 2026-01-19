from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


class UserProfile(models.Model):
    """
    Extended user profile for North American users seeking medical trips to China.
    Links to Django's built-in User model for authentication.
    """
    # Link to Django's User model (one-to-one relationship)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    
    # Phone number validation for North American format (e.g., +1-234-567-8900)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        help_text="North American phone number"
    )
    
    # Language preference for communication
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('zh-cn', 'Chinese (Simplified)'),
        ('zh-tw', 'Chinese (Traditional)'),
    ]
    language_preference = models.CharField(
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default='en',
        help_text="Preferred language for communication"
    )
    
    # Basic medical history
    medical_history = models.TextField(
        blank=True,
        help_text="Basic medical history, allergies, current medications, etc."
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.username} - Profile"


class ChinaDoctor(models.Model):
    """
    Represents doctors in Chinese hospitals available for tele-consultation.
    """
    # Doctor's full name
    name = models.CharField(
        max_length=200,
        help_text="Doctor's full name (in English or pinyin)"
    )
    
    # Hospital affiliation
    hospital = models.CharField(
        max_length=300,
        help_text="Hospital name (e.g., Peking Union Medical College Hospital)"
    )
    
    # Medical department/specialty
    DEPARTMENT_CHOICES = [
        ('cardiology', 'Cardiology'),
        ('neurology', 'Neurology'),
        ('orthopedics', 'Orthopedics'),
        ('oncology', 'Oncology'),
        ('gastroenterology', 'Gastroenterology'),
        ('endocrinology', 'Endocrinology'),
        ('dermatology', 'Dermatology'),
        ('ophthalmology', 'Ophthalmology'),
        ('ent', 'ENT (Ear, Nose, Throat)'),
        ('general', 'General Medicine'),
        ('other', 'Other'),
    ]
    department = models.CharField(
        max_length=50,
        choices=DEPARTMENT_CHOICES,
        help_text="Medical department/specialty"
    )
    
    # English biography
    biography_en = models.TextField(
        help_text="Doctor's biography in English including qualifications, experience, and expertise"
    )
    
    # Availability status
    is_available = models.BooleanField(
        default=True,
        help_text="Whether the doctor is currently accepting consultations"
    )
    
    # Years of experience
    years_of_experience = models.PositiveIntegerField(
        default=0,
        help_text="Years of medical practice experience"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['department', 'name']
        verbose_name = 'China Doctor'
        verbose_name_plural = 'China Doctors'
    
    def __str__(self):
        return f"Dr. {self.name} - {self.hospital} ({self.get_department_display()})"


class Consultation(models.Model):
    """
    Represents a tele-consultation booking between a user and a Chinese doctor.
    Includes AI triage suggestions and booking status.
    """
    # Link to user profile
    user_profile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='consultations',
        help_text="User requesting the consultation"
    )
    
    # Link to Chinese doctor
    doctor = models.ForeignKey(
        ChinaDoctor,
        on_delete=models.CASCADE,
        related_name='consultations',
        help_text="Doctor assigned to the consultation"
    )
    
    # User's symptom description
    symptoms_description = models.TextField(
        help_text="Detailed description of symptoms provided by the user"
    )
    
    # AI triage suggestion result
    ai_suggestion = models.JSONField(
        blank=True,
        null=True,
        help_text="AI-generated triage analysis and department suggestion"
    )
    
    # Consultation status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current status of the consultation"
    )
    
    # Scheduled consultation datetime
    scheduled_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Scheduled date and time for the consultation"
    )
    
    # Additional notes
    notes = models.TextField(
        blank=True,
        help_text="Additional notes or comments about the consultation"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the consultation request was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last update timestamp"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Consultation'
        verbose_name_plural = 'Consultations'
    
    def __str__(self):
        return f"Consultation #{self.id} - {self.user_profile.user.username} with Dr. {self.doctor.name} ({self.get_status_display()})"
