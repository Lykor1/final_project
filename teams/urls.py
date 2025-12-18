from django.urls import path

from . import views

app_name = 'teams'
urlpatterns = [
    path('create/', views.TeamCreateAPIView.as_view(), name='create'),
]
