from django.shortcuts import render, get_object_or_404

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
