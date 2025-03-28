# library/auth_views.py
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
import re
from .auth_models import User
import logging
logger = logging.getLogger(__name__)

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(min_length = 4, max_length=150, required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(min_length=8, max_length = 35, required=True)

    def validate_username(self, value):
        # Ensure username contains only alphanumeric characters and underscores
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError("Username must contain only letters, numbers, and underscores.")
        if User.find_by_username(value):
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate_email(self, value):
        # Check if email is already in use (assuming User model has a method for this)
        if User.find_by_email(value):  # Add this method to User model if not present
            raise serializers.ValidationError("Email already exists.")
        return value
    
    def validate_password(self, value):
        # Ensure password meets complexity requirements
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Password must contain at least one number.")
        return value
    
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(required=True)

@api_view(["POST"])
@permission_classes([AllowAny])
# @authentication_classes([])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({"errors": serializer.errors}, status=400)

    username = serializer.validated_data["username"]
    email = serializer.validated_data["email"]
    password = serializer.validated_data["password"]

    user_id = User.create_user(username, email, password)
    refresh = RefreshToken()
    refresh["user_id"] = user_id
    access = refresh.access_token
    logger.debug(f"Generated token payload: {refresh.payload}")
    return Response({
        "id": user_id,
        "refresh": str(refresh),
        "access": str(access),
    })

@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    """Authenticate user and return JWT token."""
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({"errors": serializer.errors}, status=400)

    username = serializer.validated_data["username"]
    password = serializer.validated_data["password"]

    user = User.find_by_username(username)
    if not user or not User.check_password(user["password"], password):
        return Response({"error": "Invalid credentials"}, status=401)

    # Manually create JWT tokens
    refresh = RefreshToken()
    refresh["user_id"] = str(user["_id"])  # Set custom payload
    access = refresh.access_token

    return Response({
        "id": str(user["_id"]),
        "refresh": str(refresh),
        "access": str(access),
    })