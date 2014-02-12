from django.shortcuts import render

def root(request):
    context = {}
    return render(request, "panel_core.html",context)

# Create your views here.

def login(request):
    context={}
    return render(request, "login.html",context)