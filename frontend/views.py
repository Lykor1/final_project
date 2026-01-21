from django.shortcuts import render


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
