from django.shortcuts import render

# Create your views here.
from .models import Vacancy
from rest_framework import generics
from .serializers import VacancySerializer
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
from rest_framework import status
from django.core.mail import send_mass_mail
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q
from .models import Resume
from .models import AcceptedResume, RejectedResume
from django.db import transaction
from .services.comparison import make_comparison
from .serializers import ResumeSerializer
from .pagination import VacancyPagination
from django.core.mail import send_mass_mail
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .models import Vacancy, AcceptedResume


class IsStaffOrSuperuser(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (request.user.is_staff or request.user.is_superuser)
        )


class IsAdminOrReadOnly(IsStaffOrSuperuser):
    def has_permission(self, request, view):
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True
        return super().has_permission(request, view)


class VacancyListCreateView(generics.ListCreateAPIView):
    serializer_class = VacancySerializer
    pagination_class = VacancyPagination
    permission_classes = [IsAdminOrReadOnly]
    def get_queryset(self):
        query=self.request.query_params.get('query', None)

        if query:
            return Vacancy.objects.filter(
                Q(title__icontains=query) |
                Q(experience__icontains=query) |
                Q(job_type__icontains=query) |
                Q(qualification__icontains=query) |
                Q(required_skills__icontains=query)
            )
        return Vacancy.objects.all()
    def perform_create(self, serializer):
            serializer.save(posted_by=self.request.user)
class VacancyRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = VacancySerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = Vacancy.objects.all()

class ResumeListCreateView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResumeSerializer
    parser_classes = [MultiPartParser, FormParser]
    def get_queryset(self):
        return Resume.objects.all()

class EvaluateResumeView(generics.GenericAPIView):

    def post(self, request, *args, **kwargs):

        vacancy_id = request.data.get("vacancy_id")

        if not vacancy_id:
            return Response(
                {"error": "vacancy_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            vacancy = Vacancy.objects.get(id=vacancy_id)

        except Vacancy.DoesNotExist:
            return Response(
                {"error": "Vacancy not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        resumes = Resume.objects.filter(vacancy=vacancy)

        if not resumes.exists():
            return Response(
                {"error": "No resumes found for this vacancy."},
                status=status.HTTP_404_NOT_FOUND
            )

        results = []

        for resume in resumes:

            try:
                evaluation = make_comparison(
                    resume.resume_file,
                    vacancy
                )
                print(f"Evaluation for Resume ID {resume.id}: {evaluation}")
                raw_decision = evaluation.get("action") or evaluation.get("decision") or ""
                decision = str(raw_decision).strip().lower()

                if decision in {"shortlist", "accepted"}:
                    AcceptedResume.objects.get_or_create(resume=resume)
                else:
                    RejectedResume.objects.get_or_create(resume=resume)

                results.append({
                    "resume_id": resume.id,
                    "name": resume.name,
                    "email": resume.email,
                    "evaluation": evaluation
                })

            except Exception as e:

                results.append({
                    "resume_id": resume.id,
                    "name": resume.name,
                    "email": resume.email,
                    "error": str(e)
                })

        return Response(
            {
                "vacancy_id": vacancy.id,
                "total_resumes": resumes.count(),
                "results": results
            },
            status=status.HTTP_200_OK
        )
class SendEmailToAcceptedCandidatesView(generics.GenericAPIView):

    permission_classes = [IsStaffOrSuperuser]

    def post(self, request, *args, **kwargs):

        print("\n========== SEND EMAIL STARTED ==========")

        vacancy_id = request.data.get("vacancy_id")

        print("Vacancy ID:", vacancy_id)

        if not vacancy_id:
            print("ERROR: vacancy_id is missing")

            return Response(
                {"error": "vacancy_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            vacancy = Vacancy.objects.get(id=vacancy_id)

            print("Vacancy found:", vacancy.title)
            print("Vacancy ID:", vacancy.id)

        except Vacancy.DoesNotExist:

            print("ERROR: Vacancy not found")

            return Response(
                {"error": "Vacancy not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        accepted_resumes = AcceptedResume.objects.filter(
            resume__vacancy=vacancy
        ).select_related("resume")

        print(
            "Accepted resumes count:",
            accepted_resumes.count()
        )

        if not accepted_resumes.exists():

            print("ERROR: No accepted resumes found")

            return Response(
                {
                    "error":
                    "No accepted resumes found for this vacancy."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        messages = []

        for accepted in accepted_resumes:

            print("\n--- Preparing email ---")
            print("Resume ID:", accepted.resume.id)
            print("Candidate:", accepted.resume.name)
            print("Email:", accepted.resume.email)

            subject = (
                f"Congratulations! You've been shortlisted for "
                f"{vacancy.title}"
            )

            message = (
                f"Dear {accepted.resume.name},\n\n"
                f"We are pleased to inform you that you have been "
                f"shortlisted for the position of {vacancy.title}.\n\n"
                f"We will contact you soon with further details.\n\n"
                f"Best regards,\n"
                f"TalentLens Team"
            )

            from_email = "sambadkhatiwada939@gmail.com"

            recipient = [accepted.resume.email]

            print("From:", from_email)
            print("Recipient:", recipient)
            print("Subject:", subject)
            print("Message:", message)

            messages.append(
                (
                    subject,
                    message,
                    from_email,
                    recipient,
                )
            )

        print("\nTotal messages prepared:", len(messages))

        try:

            print("Attempting to send emails...")

            send_mass_mail(
                messages,
                fail_silently=False
            )

            print("Emails sent successfully!")

        except Exception as e:

            print("\n========== EMAIL ERROR ==========")
            print("Error type:", type(e).__name__)
            print("Error:", str(e))
            print("Error repr:", repr(e))
            print("=================================\n")

            return Response(
                {
                    "error": "Failed to send emails.",
                    "details": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        print("========== SEND EMAIL FINISHED ==========\n")

        return Response(
            {
                "message": "Emails sent successfully.",
                "total_sent": len(messages)
            },
            status=status.HTTP_200_OK
        )
class GetSubmittedResumesView(generics.ListAPIView):
    serializer_class = ResumeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Resume.objects.filter(email=self.request.user.email)

class GetAcceptedResumesView(generics.ListAPIView):
    serializer_class = ResumeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        vacancy_id = self.request.query_params.get('vacancy_id')
        queryset = Resume.objects.filter(acceptedresume__isnull=False)
        if vacancy_id:
            queryset = queryset.filter(vacancy_id=vacancy_id)
        return queryset.distinct()

class GetRejectedResumesView(generics.ListAPIView):
    serializer_class = ResumeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        vacancy_id = self.request.query_params.get('vacancy_id')
        queryset = Resume.objects.filter(rejectedresume__isnull=False)
        if vacancy_id:
            queryset = queryset.filter(vacancy_id=vacancy_id)
        return queryset.distinct()