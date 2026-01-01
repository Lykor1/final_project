from django.urls import path

from . import views

app_name = 'evaluations'
urlpatterns = [
    path('<int:task_id>/create/', views.EvaluationCreateView.as_view(), name='create'),
]