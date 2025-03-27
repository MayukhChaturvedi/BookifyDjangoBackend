# library/auth_views.py
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .auth_models import User
import logging
logger = logging.getLogger(__name__)

@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])
def register(request):
    username = request.data.get("username")
    email = request.data.get("email")
    password = request.data.get("password")

    if User.find_by_username(username):
        return Response({"error": "Username already exists"}, status=400)

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
    username = request.data.get("username")
    password = request.data.get("password")

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