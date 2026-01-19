from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics
from django.shortcuts import get_object_or_404

from .models import UserProfile, ChinaDoctor, Consultation
from .serializers import (
    UserProfileSerializer,
    ChinaDoctorSerializer,
    ConsultationSerializer,
    AITriageRequestSerializer,
    AITriageResponseSerializer
)


class AITriageView(APIView):
    """
    AI-driven triage view for symptom analysis.
    
    Accepts POST requests with symptom descriptions and returns
    suggested medical department and reasoning.
    
    Endpoint: POST /api/triage/
    Request Body: {"symptoms": "description of symptoms"}
    Response: {"suggested_department": "...", "reason": "...", "confidence": 0.85}
    """
    permission_classes = [AllowAny]  # Allow unauthenticated access for initial triage
    
    def post(self, request):
        """
        Process symptom description and return AI triage suggestion.
        
        Args:
            request: HTTP request containing symptoms in the body
            
        Returns:
            JSON response with suggested department and reasoning
        """
        # Validate incoming request data
        request_serializer = AITriageRequestSerializer(data=request.data)
        
        if not request_serializer.is_valid():
            return Response(
                request_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get validated symptom description
        symptoms = request_serializer.validated_data['symptoms']
        
        # Mock AI logic - analyze symptoms and suggest department
        # TODO: Replace with actual AI/ML model integration (e.g., OpenAI, custom model)
        ai_suggestion = self._mock_ai_analysis(symptoms)
        
        # Serialize and return response
        response_serializer = AITriageResponseSerializer(data=ai_suggestion)
        
        if response_serializer.is_valid():
            return Response(
                response_serializer.validated_data,
                status=status.HTTP_200_OK
            )
        
        # Fallback in case of serialization error
        return Response(
            ai_suggestion,
            status=status.HTTP_200_OK
        )
    
    def _mock_ai_analysis(self, symptoms):
        """
        Mock AI analysis logic for symptom triage.
        
        This is a placeholder implementation. In production, this would be
        replaced with actual AI/ML model integration.
        
        Args:
            symptoms (str): User's symptom description
            
        Returns:
            dict: Dictionary containing suggested_department, reason, and confidence
        """
        symptoms_lower = symptoms.lower()
        
        # Simple keyword-based mock logic
        if any(keyword in symptoms_lower for keyword in ['chest pain', 'heart', 'palpitation', 'cardiac']):
            return {
                'suggested_department': 'Cardiology',
                'reason': 'Based on your description of chest pain and cardiac symptoms, we recommend consultation with a cardiologist for proper evaluation.',
                'confidence': 0.85
            }
        
        elif any(keyword in symptoms_lower for keyword in ['headache', 'migraine', 'dizzy', 'seizure', 'numbness']):
            return {
                'suggested_department': 'Neurology',
                'reason': 'Your symptoms suggest a neurological concern. A neurologist can help diagnose and treat conditions related to the nervous system.',
                'confidence': 0.80
            }
        
        elif any(keyword in symptoms_lower for keyword in ['joint pain', 'back pain', 'fracture', 'bone', 'arthritis']):
            return {
                'suggested_department': 'Orthopedics',
                'reason': 'Based on your musculoskeletal symptoms, an orthopedic specialist would be most appropriate for evaluation and treatment.',
                'confidence': 0.82
            }
        
        elif any(keyword in symptoms_lower for keyword in ['stomach', 'abdominal', 'nausea', 'digestive', 'bowel']):
            return {
                'suggested_department': 'Gastroenterology',
                'reason': 'Your digestive symptoms indicate that a gastroenterologist consultation would be beneficial for proper diagnosis.',
                'confidence': 0.78
            }
        
        elif any(keyword in symptoms_lower for keyword in ['skin', 'rash', 'acne', 'itching', 'dermatology']):
            return {
                'suggested_department': 'Dermatology',
                'reason': 'Your skin-related symptoms suggest consultation with a dermatologist for appropriate treatment.',
                'confidence': 0.83
            }
        
        elif any(keyword in symptoms_lower for keyword in ['eye', 'vision', 'sight', 'blind']):
            return {
                'suggested_department': 'Ophthalmology',
                'reason': 'Your vision-related symptoms require evaluation by an ophthalmologist.',
                'confidence': 0.86
            }
        
        elif any(keyword in symptoms_lower for keyword in ['ear', 'nose', 'throat', 'hearing', 'sinus']):
            return {
                'suggested_department': 'ENT (Ear, Nose, Throat)',
                'reason': 'Based on your ENT-related symptoms, consultation with an ENT specialist is recommended.',
                'confidence': 0.81
            }
        
        else:
            # Default to general medicine if no specific keywords match
            return {
                'suggested_department': 'General Medicine',
                'reason': 'Based on your symptoms, we recommend starting with a general medicine consultation for initial evaluation and potential referral to a specialist if needed.',
                'confidence': 0.70
            }


class UserProfileListCreateView(generics.ListCreateAPIView):
    """
    List all user profiles or create a new user profile.
    
    GET: List all user profiles
    POST: Create a new user profile
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        """
        Override to automatically link the profile to the authenticated user.
        """
        serializer.save(user=self.request.user)


class UserProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific user profile.
    
    GET: Retrieve user profile details
    PUT/PATCH: Update user profile
    DELETE: Delete user profile
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]


class ChinaDoctorListView(generics.ListAPIView):
    """
    List all available Chinese doctors.
    
    GET: List all doctors (optionally filter by department)
    Query Parameters:
        - department: Filter by medical department (e.g., ?department=cardiology)
        - available: Filter by availability (e.g., ?available=true)
    """
    queryset = ChinaDoctor.objects.all()
    serializer_class = ChinaDoctorSerializer
    permission_classes = [AllowAny]  # Allow public access to doctor listings
    
    def get_queryset(self):
        """
        Optionally filter doctors by department and availability.
        """
        queryset = super().get_queryset()
        
        # Filter by department if provided
        department = self.request.query_params.get('department', None)
        if department:
            queryset = queryset.filter(department=department)
        
        # Filter by availability if provided
        available = self.request.query_params.get('available', None)
        if available is not None:
            is_available = available.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(is_available=is_available)
        
        return queryset


class ChinaDoctorDetailView(generics.RetrieveAPIView):
    """
    Retrieve details of a specific Chinese doctor.
    
    GET: Retrieve doctor details by ID
    """
    queryset = ChinaDoctor.objects.all()
    serializer_class = ChinaDoctorSerializer
    permission_classes = [AllowAny]


class ConsultationListCreateView(generics.ListCreateAPIView):
    """
    List all consultations or create a new consultation.
    
    GET: List all consultations (filtered by authenticated user)
    POST: Create a new consultation
    """
    serializer_class = ConsultationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Return consultations for the authenticated user only.
        """
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        return Consultation.objects.filter(user_profile=user_profile)
    
    def perform_create(self, serializer):
        """
        Create consultation with additional context.
        """
        # You can add additional logic here, such as sending notifications
        serializer.save()


class ConsultationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific consultation.
    
    GET: Retrieve consultation details
    PUT/PATCH: Update consultation (e.g., change status, add notes)
    DELETE: Cancel/delete consultation
    """
    serializer_class = ConsultationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Return consultations for the authenticated user only.
        """
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        return Consultation.objects.filter(user_profile=user_profile)
