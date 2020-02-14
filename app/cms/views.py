from django.shortcuts import render
from django.views.defaults import permission_denied

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


def error_403(request, exception):
    if request.path.startswith('/admin/cms'):
        return render(request, 'admin/cms/403.html', status=403)

    return permission_denied(request, exception)
