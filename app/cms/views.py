from django.shortcuts import render

# Create your views here.
import json

from django.http import HttpResponse
from oauth2_provider.views import ScopedProtectedResourceView


class OAuthUserInfo(ScopedProtectedResourceView):
    required_scopes = ['user']

    """
    A GET endpoint that needs OAuth2 authentication
    and returns user info
    """
    def get(self, request, *args, **kwargs):
        user = request.user
        openid_user = {
            'sub': user.id,
            'name': user.username,
            'email': user.email,
        }
        return HttpResponse(json.dumps(openid_user), content_type='application/json')
