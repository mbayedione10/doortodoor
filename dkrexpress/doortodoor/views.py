from django.shortcuts import render

# Create your views here.
from django.views import View


class Index(View):
    def get(self,request, *args, **kwargs):
        return render(request,'doortodoor/index.html')


class About(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'doortodoor/about.html')