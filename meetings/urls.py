from django.urls import path

from . import views

app_name = 'meetings'
urlpatterns = [
    path('create/', views.MeetingCreateView.as_view(), name='create'),
]