from django.shortcuts import render

# Create your views here.
from django.views import View
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.utils.timezone import datetime

class Index(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self,request, *args, **kwargs):
        return render(request,'doortodoor/index.html')
    
    def test_func(self):
        return self.request.user.groups.all() #filter(name='Clients') 


class About(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'doortodoor/about.html')

class AjouterLivraison(LoginRequiredMixin, UserPassesTestMixin, View):
    def post(self, request, *args, **kwargs):
        """
        Formulaire qui permet d'ajouter des livraisons
        """
        libelle = request.POST.get('libelle')
        email = request.POST.get('email')
