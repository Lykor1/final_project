from django.urls import path

from . import views

app_name = 'meetings'
urlpatterns = [
    path('create/', views.MeetingCreateView.as_view(), name='create'),
    path('list/', views.MeetingListView.as_view(), name='list'),
    path('<int:pk>/delete/', views.MeetingDeleteView.as_view(), name='delete'),
    path('<int:pk>/update/', views.MeetingUpdateView.as_view(), name='update'),
]
