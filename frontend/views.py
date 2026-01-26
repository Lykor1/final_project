from django.shortcuts import render, get_object_or_404

from meetings.models import Meeting
from tasks.models import Task
from teams.models import Team


def index(request):
    return render(request, 'index.html')


def users_register(request):
    return render(request, 'users/register.html')


def users_login(request):
    return render(request, 'users/login.html')


def users_detail(request):
    return render(request, 'users/detail.html')


def users_list(request):
    return render(request, 'users/list.html')


def teams_create(request):
    return render(request, 'teams/create.html')


def teams_list(request):
    return render(request, 'teams/list.html')


def teams_change_role(request, team_id):
    team = get_object_or_404(Team, pk=team_id)
    return render(request, 'teams/change_role.html', {'team': team})


def teams_update(request, team_id):
    team = get_object_or_404(Team, pk=team_id)
    return render(request, 'teams/update.html', {'team': team})


def teams_detail(request):
    return render(request, 'teams/detail.html')


def tasks_create(request, team_id):
    team = get_object_or_404(Team, pk=team_id)
    return render(request, 'tasks/create.html', {'team': team})


def tasks_admin_list(request):
    return render(request, 'tasks/admin_list.html')


def tasks_own_list(request):
    return render(request, 'tasks/own_list.html')


def tasks_update(request, team_id, pk):
    task = get_object_or_404(Task, pk=pk, team=team_id)
    return render(request, 'tasks/update.html', {'task': task})

def meetings_create(request):
    return render(request, 'meetings/create.html')

def meetings_list(request):
    return render(request, 'meetings/list.html')

def meetings_update(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    return render(request, 'meetings/update.html', {'meeting': meeting})

def calendars_list(request):
    return render(request, 'calendars/list.html')