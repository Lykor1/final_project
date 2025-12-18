from django.urls import path

from . import views

app_name = 'teams'
urlpatterns = [
    path('create/', views.TeamCreateAPIView.as_view(), name='create'),
    path('delete/<int:pk>', views.TeamDeleteAPIView.as_view(), name='delete'),
]
