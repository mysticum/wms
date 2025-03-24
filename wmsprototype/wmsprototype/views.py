from django.http import HttpResponse
from django.shortcuts import render

def home(request):
  return render(request, "home.html")

def actions(request):
  return render(request, "actions.html")