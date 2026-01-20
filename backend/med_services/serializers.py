from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Avg, Count
from .models import UserProfile, ChinaDoctor, Consultation, DoctorAvailability, DoctorReview


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
    average_rating = serializers.SerializerMethodField(help_text="Average rating from completed consultations")
    review_count = serializers.SerializerMethodField(help_text="Number of reviews")
    
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
            'average_rating',
            'review_count',
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

    def get_average_rating(self, obj):
        agg = DoctorReview.objects.filter(consultation__doctor=obj).aggregate(avg=Avg('stars'))
        return round(agg['avg'], 2) if agg['avg'] is not None else None

    def get_review_count(self, obj):
        return DoctorReview.objects.filter(consultation__doctor=obj).count()


class ConsultationSerializer(serializers.ModelSerializer):
    """
    Serializer for Consultation model.
    Includes nested user profile and doctor information for complete consultation details.
    """
    # Nested serializers for related objects
    user_profile = UserProfileSerializer(read_only=True)
    doctor = ChinaDoctorSerializer(read_only=True)
    
    # Write-only fields for creating consultations
    user_profile_id = serializers.IntegerField(write_only=True, required=False, help_text="User profile id (optional, defaults to current user)")
    doctor_id = serializers.IntegerField(write_only=True, help_text="Doctor id for this consultation")

    # Optional report upload
    report_file = serializers.FileField(required=False, allow_null=True, help_text="Optional report file (PDF/JPG/PNG)")
    
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
            'report_file',
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
        request = self.context.get('request')
        if request is None:
            return data

        # On update: handle status transitions
        if self.instance is not None and 'status' in data:
            if not request.user.is_staff:
                raise serializers.ValidationError({'status': 'Only assigned doctor or admin can update status'})

            current = self.instance.status
            target = data.get('status', current)
            allowed = {
                'pending': {'confirmed', 'cancelled'},
                'confirmed': {'completed', 'cancelled'},
                'completed': set(),
                'cancelled': set(),
            }
            if target == current:
                return data
            if target not in allowed.get(current, set()):
                raise serializers.ValidationError({'status': f'Cannot change status from {current} to {target}'})

        # On create
        if self.instance is None:
            doctor_id = data.get('doctor_id')
            scheduled_at = data.get('scheduled_at')
            user_profile_id = data.get('user_profile_id')

            # Resolve and validate doctor
            try:
                doctor = ChinaDoctor.objects.get(id=doctor_id)
            except ChinaDoctor.DoesNotExist:
                raise serializers.ValidationError({'doctor_id': 'Doctor not found'})

            if not doctor.is_available:
                raise serializers.ValidationError({'doctor_id': 'This doctor is currently not available for consultations'})

            # Resolve user profile; enforce ownership
            if user_profile_id:
                try:
                    user_profile = UserProfile.objects.get(id=user_profile_id)
                except UserProfile.DoesNotExist:
                    raise serializers.ValidationError({'user_profile_id': 'User profile not found'})
                if not request.user.is_staff and user_profile.user != request.user:
                    raise serializers.ValidationError({'user_profile_id': 'User profile does not belong to the authenticated user'})
            else:
                try:
                    user_profile = UserProfile.objects.get(user=request.user)
                    data['user_profile_id'] = user_profile.id
                except UserProfile.DoesNotExist:
                    raise serializers.ValidationError({'user_profile_id': 'User profile not found for current user'})

            # Scheduling validation
            if scheduled_at:
                scheduled_at = timezone.make_aware(scheduled_at) if timezone.is_naive(scheduled_at) else scheduled_at
                schedule_date = scheduled_at.date()
                schedule_time = scheduled_at.time()

                # Check doctor availability window
                availability_exists = DoctorAvailability.objects.filter(
                    doctor=doctor,
                    date=schedule_date,
                    start_time__lte=schedule_time,
                    end_time__gt=schedule_time
                ).exists()
                if not availability_exists:
                    raise serializers.ValidationError({'scheduled_at': 'Selected time is outside doctor availability'})

                # Prevent confirmed double booking at same time slot
                if Consultation.objects.filter(
                    doctor=doctor,
                    status='confirmed',
                    scheduled_at=scheduled_at
                ).exists():
                    raise serializers.ValidationError({'scheduled_at': 'This time slot is already booked for this doctor'})

        return data

    def create(self, validated_data):
        request = self.context['request']
        doctor_id = validated_data.pop('doctor_id')
        user_profile_id = validated_data.pop('user_profile_id', None)

        doctor = ChinaDoctor.objects.get(id=doctor_id)

        if user_profile_id:
            user_profile = UserProfile.objects.get(id=user_profile_id)
            if not request.user.is_staff and user_profile.user != request.user:
                raise serializers.ValidationError({'user_profile_id': 'User profile does not belong to the authenticated user'})
        else:
            try:
                user_profile = UserProfile.objects.get(user=request.user)
            except UserProfile.DoesNotExist:
                raise serializers.ValidationError({'user_profile_id': 'User profile not found for current user'})

        return Consultation.objects.create(
            user_profile=user_profile,
            doctor=doctor,
            **validated_data
        )

    def update(self, instance, validated_data):
        status_value = validated_data.pop('status', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if status_value:
            instance.status = status_value

        instance.save()
        return instance


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


class DoctorAvailabilitySerializer(serializers.ModelSerializer):
    """Serializer for DoctorAvailability model."""

    doctor = ChinaDoctorSerializer(read_only=True)
    doctor_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = DoctorAvailability
        fields = [
            'id',
            'doctor',
            'doctor_id',
            'date',
            'start_time',
            'end_time',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DoctorReviewSerializer(serializers.ModelSerializer):
    """Serializer for doctor reviews."""

    consultation = ConsultationSerializer(read_only=True)
    stars = serializers.IntegerField(min_value=1, max_value=5, help_text="Rating stars (1-5)")
    comment = serializers.CharField(required=False, allow_blank=True, help_text="Optional review comment")

    class Meta:
        model = DoctorReview
        fields = ['id', 'consultation', 'stars', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'consultation']

    def validate(self, attrs):
        consultation = self.context.get('consultation')
        if consultation is None:
            raise serializers.ValidationError({'consultation': 'Consultation is required'})

        if consultation.status != 'completed':
            raise serializers.ValidationError({'consultation': 'Only completed consultations can be reviewed'})

        if hasattr(consultation, 'review'):
            raise serializers.ValidationError({'consultation': 'This consultation already has a review'})

        request = self.context.get('request')
        if request and not request.user.is_staff:
            if consultation.user_profile.user != request.user:
                raise serializers.ValidationError({'consultation': 'You cannot review another user consultation'})

        return attrs


class RegisterSerializer(serializers.Serializer):
    """
    Serializer for user registration.
    Automatically creates User and UserProfile upon successful validation.
    """
    username = serializers.CharField(
        max_length=150,
        help_text="Unique username for login"
    )
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'},
        help_text="Password (min 8 characters)"
    )
    email = serializers.EmailField(
        required=True,
        help_text="User email address"
    )
    phone = serializers.CharField(
        max_length=17,
        help_text="North American phone number (e.g., +12345678901)"
    )
    language_preference = serializers.ChoiceField(
        choices=['en', 'zh-cn', 'zh-tw'],
        default='en',
        help_text="Preferred language"
    )
    
    def validate_username(self, value):
        """Ensure username is unique."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value
    
    def validate_email(self, value):
        """Ensure email is unique."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value
    
    def validate_phone(self, value):
        """Validate North American phone format."""
        import re
        pattern = r'^\+?1?\d{10,15}$'
        if not re.match(pattern, value):
            raise serializers.ValidationError(
                "Phone number must be in North American format (e.g., +12345678901)"
            )
        return value
    
    def create(self, validated_data):
        """
        Create User and automatically create linked UserProfile.
        Returns the created user with profile attached.
        """
        phone = validated_data.pop('phone')
        language_preference = validated_data.pop('language_preference', 'en')
        
        # Create user securely
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        
        # Automatically create linked UserProfile
        UserProfile.objects.create(
            user=user,
            phone=phone,
            language_preference=language_preference
        )
        
        return user
