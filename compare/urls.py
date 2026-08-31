from django.urls import path
from .views import (
    VacancyListCreateView,
    VacancyRetrieveUpdateDestroyView,
    ResumeListCreateView,
    EvaluateResumeView,
    SendEmailToAcceptedCandidatesView,
    GetSubmittedResumesView,
    GetAcceptedResumesView,
    GetRejectedResumesView
)

urlpatterns = [
    path('vacancies/', VacancyListCreateView.as_view(), name='listcreate'),
    path('vacancies/<int:pk>/', VacancyRetrieveUpdateDestroyView.as_view(), name='retrievedeleteupdate'),
    path('resumes/', ResumeListCreateView.as_view(), name='resumelistcreate'),
    path('evaluate/', EvaluateResumeView.as_view(), name='evaluate-resume'),
    path('send-email/', SendEmailToAcceptedCandidatesView.as_view(), name='send-email-to-accepted'),
    path('submitted-resumes/', GetSubmittedResumesView.as_view(), name='submitted-resumes'),
    path('accepted-resumes/', GetAcceptedResumesView.as_view(), name='accepted-resumes'),
    path('rejected-resumes/', GetRejectedResumesView.as_view(), name='rejected-resumes'),
]