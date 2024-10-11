from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

class SessionJWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        jwt_token = request.session.get('jwt_token')
        if jwt_token:
            try:
                validated_token = JWTAuthentication().get_validated_token(jwt_token)
                request.user = JWTAuthentication().get_user(validated_token)
            except AuthenticationFailed:
                pass  # Handle token validation failure if needed
