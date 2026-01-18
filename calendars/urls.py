from django.urls import path

from . import views

app_name = 'calendars'
urlpatterns = [
    path('', views.CalendarListView.as_view(), name='calendar')
]
