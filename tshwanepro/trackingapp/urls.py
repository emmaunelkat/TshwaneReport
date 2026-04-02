from django.urls import path
from . import views

app_name = 'trackingapp'

urlpatterns = [
    path('', views.track_report, name='track_report'),
]
