from django.shortcuts import render


def index(request):
    return render(request, 'index.html')


def users_register(request):
    return render(request, 'users/register.html')
