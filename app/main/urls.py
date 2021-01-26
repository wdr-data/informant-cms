"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url
from django.urls import path, include
from django.views.generic.base import RedirectView
from django.conf.urls.static import static
from django.conf import settings
from api.urls import router
import cms.views as cms_views

urlpatterns = [
    path("admin/", admin.site.urls),
    url(r"^$", RedirectView.as_view(url="/admin/")),
    url(r"^admin/cms/push/", RedirectView.as_view(url="/admin/cms/pushcompact/")),
    url(
        r"^tags_input/",
        include(("tags_input.urls", "tags_input"), namespace="tags_input"),
    ),
    url(r"^api-docs/", include("rest_framework.urls")),
    url(r"^api/v1/", include(router.urls)),
    url(r"^tz_detect/", include("tz_detect.urls")),
    url(r"^oauth/user", cms_views.OAuthUserInfo.as_view()),
    url(r"^oauth/", include("oauth2_provider.urls", namespace="oauth2_provider")),
    url(r"^s3direct/", include("s3direct.urls")),
]

if settings.MEDIA_URL and settings.MEDIA_ROOT:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler403 = cms_views.error_403
