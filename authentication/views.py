from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from .serializers import UserSerializer
from .serializers import LoginSerializer
class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer
    queryset = User.objects.all()
class LoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(username=serializer.validated_data['username'], password=serializer.validated_data['password'])
        if user is None:
            return Response(
                {"detail": "Invalid username or password"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        refresh = RefreshToken.for_user(user)
        is_admin = bool(user.is_staff or user.is_superuser or user.username.strip().lower() == 'admin')
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'is_admin': is_admin,
            'isAdmin': is_admin,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_admin': is_admin,
                'isAdmin': is_admin,
            },
        })
@api_view(['POST'])
@permission_classes([AllowAny])
def logout(request):
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "Successfully logged out"},status=status.HTTP_205_RESET_CONTENT)
    except Exception as e:
        return Response({"message": "Invalid refresh token"},status=status.HTTP_400_BAD_REQUEST)