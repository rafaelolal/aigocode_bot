from django.urls import path
from .views import *

app_name = 'api'

urlpatterns = [
    path('', auth_api, name='auth_api'),
    path('another_endpoint', another_endpoint, name='another_endpoint')
]