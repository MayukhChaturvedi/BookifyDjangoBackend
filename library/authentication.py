# library/authentication.py
# import logging
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from .auth_models import User

# logger = logging.getLogger(__name__)

class MongoJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # logger.debug("Starting authentication process")
        header = self.get_header(request)
        # logger.debug(f"Authorization header: {header}")
        if header is None:
            # logger.debug("No Authorization header found")
            return None

        raw_token = self.get_raw_token(header)
        # logger.debug(f"Raw token: {raw_token}")
        if raw_token is None:
            # logger.debug("No valid token in header")
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            # logger.debug(f"Validated token: {validated_token}")
        except InvalidToken as e:
            # logger.error(f"Token validation failed: {str(e)}")
            raise AuthenticationFailed("Invalid token", code="authentication_failed")

        user = self.get_user(validated_token)
        # logger.debug(f"Authenticated user: {user.id}")
        return (user, validated_token)

    def get_user(self, validated_token):
        # logger.debug(f"Token payload: {validated_token}")
        try:
            user_id = validated_token["user_id"]
            # logger.debug(f"Fetching user with ID: {user_id}")
            user_data = User.find_by_id(user_id)
            # logger.debug(f"User data from MongoDB: {user_data}")
            if not user_data:
                # logger.error(f"No user found for ID: {user_id}")
                raise AuthenticationFailed("User not found", code="user_not_found")

            class MongoUser:
                def __init__(self, user_id, user_data):
                    self.id = user_id
                    self.username = user_data.get("username", "")
                    self.email = user_data.get("email", "")
                    self.is_authenticated = True
                    self.is_active = True
                    self.is_anonymous = False

                def __str__(self):
                    return self.username

            return MongoUser(user_id, user_data)
        except KeyError:
            # logger.error("Token missing user_id")
            raise InvalidToken("Token contained no recognizable user identification")
        except Exception as e:
            # logger.error(f"Error fetching user: {str(e)}")
            raise AuthenticationFailed(f"Error fetching user: {str(e)}")