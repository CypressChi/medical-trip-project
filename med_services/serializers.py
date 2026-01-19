from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, ChinaDoctor, Consultation


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for Django's built-in User model.
    Used for basic user information in API responses.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for UserProfile model.
    Includes nested user information for complete profile data.
    """
    # Nested serializer to include user details
    user = UserSerializer(read_only=True)
    
    # Display the readable language choice
    language_preference_display = serializers.CharField(
        source='get_language_preference_display',
        read_only=True
    )
    
    class Meta:
        model = UserProfile
        fields = [
            'id',
            'user',
            'phone',
            'language_preference',
            'language_preference_display',
            'medical_history',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_phone(self, value):
        """
        Custom validation for phone number field.
        Ensures proper North American format.
        """
        if value and not value.startswith('+'):
            raise serializers.ValidationError(
                "Phone number should include country code (e.g., +1 for North America)"
            )
        return value


class ChinaDoctorSerializer(serializers.ModelSerializer):
    """
    Serializer for ChinaDoctor model.
    Converts doctor information to JSON for mobile app consumption.
    """
    # Display the readable department choice
    department_display = serializers.CharField(
        source='get_department_display',
        read_only=True
    )
    
    class Meta:
        model = ChinaDoctor
        fields = [
            'id',
            'name',
            'hospital',
            'department',
            'department_display',
            'biography_en',
            'is_available',
            'years_of_experience',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_years_of_experience(self, value):
        """
        Validate that years of experience is reasonable.
        """
        if value < 0:
            raise serializers.ValidationError("Years of experience cannot be negative")
        if value > 70:
            raise serializers.ValidationError("Years of experience seems unrealistic")
        return value


class ConsultationSerializer(serializers.ModelSerializer):
    """
    Serializer for Consultation model.
    Includes nested user profile and doctor information for complete consultation details.
    """
    # Nested serializers for related objects
    user_profile = UserProfileSerializer(read_only=True)
    doctor = ChinaDoctorSerializer(read_only=True)
    
    # Write-only fields for creating consultations
    user_profile_id = serializers.IntegerField(write_only=True)
    doctor_id = serializers.IntegerField(write_only=True)
    
    # Display the readable status choice
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    class Meta:
        model = Consultation
        fields = [
            'id',
            'user_profile',
            'user_profile_id',
            'doctor',
            'doctor_id',
            'symptoms_description',
            'ai_suggestion',
            'status',
            'status_display',
            'scheduled_at',
            'notes',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_symptoms_description(self, value):
        """
        Ensure symptom description is detailed enough.
        """
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Please provide a more detailed description of your symptoms (at least 10 characters)"
            )
        return value
    
    def validate(self, data):
        """
        Object-level validation to check doctor availability and user profile existence.
        """
        # Check if doctor exists and is available (only during creation)
        if self.instance is None:  # Only validate on creation
            doctor_id = data.get('doctor_id')
            if doctor_id:
                try:
                    doctor = ChinaDoctor.objects.get(id=doctor_id)
                    if not doctor.is_available:
                        raise serializers.ValidationError({
                            'doctor_id': 'This doctor is currently not available for consultations'
                        })
                except ChinaDoctor.DoesNotExist:
                    raise serializers.ValidationError({
                        'doctor_id': 'Doctor not found'
                    })
            
            # Check if user profile exists
            user_profile_id = data.get('user_profile_id')
            if user_profile_id:
                try:
                    UserProfile.objects.get(id=user_profile_id)
                except UserProfile.DoesNotExist:
                    raise serializers.ValidationError({
                        'user_profile_id': 'User profile not found'
                    })
        
        return data


class AITriageRequestSerializer(serializers.Serializer):
    """
    Serializer for AI Triage request.
    Accepts user's symptom description for AI analysis.
    """
    symptoms = serializers.CharField(
        max_length=2000,
        help_text="Detailed description of symptoms"
    )
    
    def validate_symptoms(self, value):
        """
        Ensure symptoms description is detailed enough for AI analysis.
        """
        if len(value.strip()) < 20:
            raise serializers.ValidationError(
                "Please provide a more detailed description of your symptoms (at least 20 characters)"
            )
        return value.strip()


class AITriageResponseSerializer(serializers.Serializer):
    """
    Serializer for AI Triage response.
    Returns suggested department and reasoning.
    """
    suggested_department = serializers.CharField(
        help_text="The medical department recommended for consultation"
    )
    reason = serializers.CharField(
        help_text="Explanation for the department suggestion"
    )
    confidence = serializers.FloatField(
        help_text="Confidence level of the suggestion (0-1)",
        required=False
    )
