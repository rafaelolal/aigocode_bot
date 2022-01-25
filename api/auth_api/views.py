from django.shortcuts import render
from rest_framework import viewsets
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .serializers import HeroSerializer
from .models import Hero

# Create your views here.
class HeroViewSet(viewsets.ModelViewSet):
    queryset = Hero.objects.all().order_by('name')
    serializer_class = HeroSerializer

@csrf_exempt
def my_view(request):
    if request.method == 'POST':
        print('SOMETHING POSTED')
        print(request.body)
        return HttpResponse("SOMETHING POSTED")


    else:
        print('NOTHING POSTED')
        return HttpResponse("NOTHING POSTED")
