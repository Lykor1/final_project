from django.urls import path

from . import views

app_name = 'teams'
urlpatterns = [
    path('create/', views.TeamCreateAPIView.as_view(), name='create'),
    path('delete/<int:pk>', views.TeamDeleteAPIView.as_view(), name='delete'),
    path('add-user/<int:team_id>/', views.TeamAddUserView.as_view(), name='add-user'),
    path('remove-user/', views.TeamRemoveUserView.as_view(), name='remove-user'),
    path('change-role/<int:team_id>/', views.TeamUpdateUserRoleView.as_view(), name='change-role'),
]
