from django.urls import path

from . import views

app_name = 'tasks'
urlpatterns = [
    path('<int:team_id>/create/', views.TaskCreateView.as_view(), name='create'),
]
