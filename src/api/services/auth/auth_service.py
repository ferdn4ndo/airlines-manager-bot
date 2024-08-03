import datetime
import os
from typing import Tuple, Dict

from django import http
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import authentication
from rest_framework import exceptions
from rest_framework.authentication import get_authorization_header

from api.models.user_model import CustomUser, UserToken
from api.services.logging import get_logger
from api.services.web import WebRequest


class UServerAuthentication(authentication.BaseAuthentication):
    """
    uServer-Auth remote validated token authentication.

    Clients should authenticate by passing the token key in the "Authorization" HTTP header, prepended with the
    string "Token ".  For example:

    Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
    """
    keyword = 'Token'

    def authenticate(self, request: http.request) -> [Tuple]:
        """
        Authenticate the request and return a two-tuple of (user, token).
        :param request:
        :return: Tuple
        """
        auth = get_authorization_header(request).split()
        logger = get_logger(__name__)

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            logger.debug("Invalid token header (no auth header)")
            return None

        if len(auth) == 1:
            logger.debug("Invalid token header (auth header words == 1)")
            msg = _('Invalid token header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            logger.debug("Invalid token header (auth header words > 2)")
            msg = _('Invalid token header. Token string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            logger.debug("Invalid token header (unicode error)")
            msg = _('Invalid token header. Token string should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def analyse_token(self, token: str):
        """
        Performs a checking in uServer-Auth against a given token
        :param token:
        :return: The json response of uServer-Auth
        """
        auth_url = self.get_auth_url()
        request = WebRequest(
            url=auth_url,
            method='GET',
            headers={
                'Authorization': 'Bearer {}'.format(token)
            }
        )
        return request.get_json_response()

    def authenticate_credentials(self, token: str) -> Tuple:
        """
        Validate a given token credential and retrieve a local user account if successful
        :param token:
        :return:
        """
        try:
            user_token = UserToken.objects.get(token=token)

            if user_token.expires_at.astimezone(timezone.utc).replace(tzinfo=None) < datetime.datetime.utcnow():
                raise exceptions.AuthenticationFailed(_("The authentication token has expired. Please log-in again or use the refresh token to retrieve a new one."))

            return user_token.user, token
        except UserToken.DoesNotExist:
            pass

        response_data = self.analyse_token(token)
        if response_data is None:
            raise exceptions.AuthenticationFailed(_("Invalid or malformed token."))
        if 'message' in response_data:
            raise exceptions.AuthenticationFailed(_(response_data['message']))
        if 'uuid' not in response_data:
            raise exceptions.AuthenticationFailed(_(response_data['message']))

        user = UServerAuthentication.create_user_from_email(email=response_data['username'])

        user_token, created = UserToken.objects.get_or_create(
            token=token,
            user=user,
            issued_at=response_data['token']['issued_at'],
            expires_at=response_data['token']['expires_at'],
        )
        user_token.save()

        return user, token

    @staticmethod
    def create_user_from_email(email: str) -> CustomUser:
        """
        Create a user (or update the existing one) based on the USever-Auth response data
        :return:
        """
        user, created = CustomUser.objects.get_or_create(email=email)
        user.last_activity_at = timezone.now()
        user.save()

        return user

    @staticmethod
    def get_auth_url(endpoint: str = 'me') -> str:
        """
        Generates the route to uServer-Auth
        :return: str The route
        """
        return 'http://{}/auth/{}'.format(os.environ['USERVER_AUTH_HOST'], endpoint)

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate` header in a `401 Unauthenticated` response.
        """
        return self.keyword

    @staticmethod
    def clear_cache():
        """
        This will force all users to re-login. Useful when changing/restarting the authentication mechanism, as
        suggested in https://docs.djangoproject.com/en/3.0/topics/auth/customizing/
        :return:
        """
        Session.objects.all().delete()

    def get_user_or_create(self, username: str, password: str):
        """
        Get a user (or create one if not exists) based on a username and password (for the current system)
        :param username:
        :param password:
        :return:
        """

        self.perform_registration(email=username, password=password)
        self.perform_login(email=username, password=password)

        return UServerAuthentication.create_user_from_email(email=username)

    def perform_registration(self, email: str, password: str) -> Dict:
        reg_url = self.get_auth_url('register')
        reg_request = WebRequest(
            url=reg_url,
            method='POST'
        )
        reg_request.set_json_payload({
            'username': email,
            'system_name': os.environ['USERVER_AUTH_SYSTEM_NAME'],
            'system_token': os.environ['USERVER_AUTH_SYSTEM_TOKEN'],
            'password': password
        })
        reg_response = reg_request.get_json_response()
        return reg_response

    def perform_login(self, email: str, password: str) -> Dict:
        login_url = self.get_auth_url('login')
        login_request = WebRequest(
            url=login_url,
            method='POST'
        )
        login_request.set_json_payload({
            'username': email,
            'system_name': os.environ['USERVER_AUTH_SYSTEM_NAME'],
            'system_token': os.environ['USERVER_AUTH_SYSTEM_TOKEN'],
            'password': password
        })
        login_response_data = login_request.get_json_response()

        if 'access_token' not in login_response_data:
            raise exceptions.AuthenticationFailed(_("Failed to login with user."))

        user, created = CustomUser.objects.get_or_create(email=email)
        user.set_password(password)
        user.save()
        login_response_data['user_id'] = user.id

        return login_response_data
