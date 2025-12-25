from django.urls import path

from . import views

app_name = 'tasks'
urlpatterns = [
    path('<int:team_id>/create/', views.TaskCreateView.as_view(), name='create'),
    path('<int:team_id>/update/<int:pk>/', views.TaskUpdateView.as_view(), name='update'),
    path('<int:team_id>/delete/<int:pk>/', views.TaskDeleteView.as_view(), name='delete'),
    path('<int:task_id>/add/', views.CommentCreateView.as_view(), name='add-comment'),
]
