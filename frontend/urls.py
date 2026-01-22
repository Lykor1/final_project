from django.urls import path

from . import views

app_name = 'frontend'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.users_register, name='users-register'),
    path('login/', views.users_login, name='users-login'),
    path('users/detail/', views.users_detail, name='users-detail'),
    path('users/list/', views.users_list, name='users-list'),
    path('teams/create/', views.teams_create, name='teams-create'),
    path('teams/list/', views.teams_list, name='teams-list'),
    path('teams/<int:team_id>/change-role/', views.teams_change_role, name='teams-change-role'),
    path('teams/<int:team_id>/update/', views.teams_update, name='teams-update'),
    path('teams/detail/', views.teams_detail, name='teams-detail'),
    path('tasks/<int:team_id>/create/', views.tasks_create, name='tasks-create'),
]
