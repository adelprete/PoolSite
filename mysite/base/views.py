from django.shortcuts import render

def root(request):
    context = {}
    return render(request, "panel_core.html",context)

# Create your views here.
