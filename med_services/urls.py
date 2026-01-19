from django.urls import path
from .views import (
    AITriageView,
    UserProfileListCreateView,
    UserProfileDetailView,
    ChinaDoctorListView,
    ChinaDoctorDetailView,
    ConsultationListCreateView,
    ConsultationDetailView
)

app_name = 'med_services'

urlpatterns = [
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
]
