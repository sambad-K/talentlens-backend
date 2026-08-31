from .models import Vacancy
from rest_framework import serializers
from .models import Resume
from .models import AcceptedResume
from .models import RejectedResume
class VacancySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacancy
        fields = '__all__'  
class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ['id', 'name', 'email', 'resume_file', 'vacancy', 'applied_at']
        read_only_fields = ['id', 'applied_at']
class AcceptedResumeSerializer(serializers.ModelSerializer):
    resume = ResumeSerializer()
    class Meta:
        model = AcceptedResume
        fields = '__all__'
class RejectedResumeSerializer(serializers.ModelSerializer):
    resume = ResumeSerializer()
    class Meta:
        model = RejectedResume
        fields = '__all__'