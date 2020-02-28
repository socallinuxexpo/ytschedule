from django.shortcuts import render

# Create your views here
from django.http import HttpResponse
from django.template import loader

from .models import Room


def index(request):
    template = loader.get_template('index.html')
    context = { }
    return HttpResponse(template.render(context, request))

def view(request):
    template = loader.get_template('view_local.html')
    context = { }
    return HttpResponse(template.render(context, request))


