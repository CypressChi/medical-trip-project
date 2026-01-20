from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView,
    AITriageView,
    UserProfileListCreateView,
    UserProfileDetailView,
    ChinaDoctorListView,
    ChinaDoctorDetailView,
    ConsultationListCreateView,
    ConsultationDetailView,
    DoctorAvailabilityListView,
    ConsultationStatusUpdateView,
    ConsultationReviewCreateView
)

app_name = 'med_services'

urlpatterns = [
    # JWT Authentication endpoints
    path('auth/login/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('auth/register/', RegisterView.as_view(), name='register'),

    # AI Triage endpoint
    path('triage/', AITriageView.as_view(), name='ai-triage'),
    
    # User Profile endpoints
    path('profiles/', UserProfileListCreateView.as_view(), name='profile-list-create'),
    path('profiles/<int:pk>/', UserProfileDetailView.as_view(), name='profile-detail'),
    
    # China Doctor endpoints
    path('doctors/', ChinaDoctorListView.as_view(), name='doctor-list'),
    path('doctors/<int:pk>/', ChinaDoctorDetailView.as_view(), name='doctor-detail'),
    
    # Consultation endpoints
    path('consultations/', ConsultationListCreateView.as_view(), name='consultation-list-create'),
    path('consultations/<int:pk>/', ConsultationDetailView.as_view(), name='consultation-detail'),
    path('consultations/<int:pk>/status/', ConsultationStatusUpdateView.as_view(), name='consultation-status'),
    path('consultations/<int:pk>/review/', ConsultationReviewCreateView.as_view(), name='consultation-review'),

    # Doctor availability endpoints
    path('doctor-availability/', DoctorAvailabilityListView.as_view(), name='doctor-availability-list'),
]
