from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import UserLoginSerializer, UserRegistrationSerializer, UserSerializer
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import  RefreshToken

class SignUpApiView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token()
        return Response({
            "access_token": access,
            "refresh_token": refresh,
            "user_serializer": UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class LoginApiView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        return Response(
            {
                "access_token": str(access),
                "refresh_token": str(refresh),
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )