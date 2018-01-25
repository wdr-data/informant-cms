from django.apps import AppConfig
from rest_framework.pagination import LimitOffsetPagination


class ApiConfig(AppConfig):
    name = 'api'


class StandardPagination(LimitOffsetPagination):
    page_size = 10
