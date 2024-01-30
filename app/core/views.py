"""
Core users views.
"""
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.utils import timezone

from rest_framework import generics, exceptions, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .authentication import JWTAuthentication
from core.models import UserToken  # noqa
from .serializers import UserSerializer, UserUpdateSerializer


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = UserSerializer


class LoginView(APIView):

    def post(self, request):  # noqa
        email = request.data['email']
        password = request.data['password']
        scope = request.data['scope']

        user = get_user_model().objects.filter(email=email).first()

        if user is None:
            raise exceptions.AuthenticationFailed(f'User not found! That email has not '
                                                  f'been registered.')

        if not user.check_password(password):
            raise exceptions.AuthenticationFailed('Incorrect Password!')

        if user.is_ambassador and scope == 'admin':
            raise exceptions.AuthenticationFailed('Unauthorized')

        token = JWTAuthentication.generate_jwt(user.id, scope)

        try:
            token = user.auth.token

        except ObjectDoesNotExist:

            UserToken.objects.create(
                user=user,
                token=token,
                expired_at=timezone.now() + timezone.timedelta(days=1)
            )

        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'success': True,
            "message": "Your login was successful",
            "data": UserUpdateSerializer(user).data,
            "jwt": token,
        }

        return response


class ManageUserView(generics.RetrieveUpdateDestroyAPIView):
    """Mange the authenticated user."""
    serializer_class = UserUpdateSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated user."""

        return self.request.user

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return JsonResponse(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():

            password = serializer.validated_data.pop('password', None)
            user = serializer.update(instance, serializer.validated_data)

            if password:
                user.set_password(password)
                user.save()

            data = serializer.validated_data

            return Response({
                "success": True,
                "message": "Profile updated successfully",
                "data": data,
            })

        else:
            return Response({"success": False, "details": serializer.errors})


class UsersAPIView(generics.ListAPIView):
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [permissions.IsAuthenticated]


class LogoutAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):  # noqa
        response = Response()
        response.delete_cookie(key='jwt')

        response.data = {
            'success': True,
            "message": "Your logout was successful"
        }

        UserToken.objects.filter(user=request.user).delete()

        return response
