from django.shortcuts import render, redirect

# Create your views here.
from django.views import View
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.utils.timezone import datetime
from django.core.mail import send_mail
from doortodoor.models import *
from doortodoor.serializers import *


class Index(LoginRequiredMixin,UserPassesTestMixin, View):
    def get(self,request, *args, **kwargs):
        return render(request,'doortodoor/index.html')
    
    def test_func(self):
        return self.request.user.groups.all() #filter(name='Clients') 


class About(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'doortodoor/about.html')
    
    def test_func(self):
        return self.request.user.groups.all()


class AjouterLivraison(LoginRequiredMixin,UserPassesTestMixin, View):

    def get(self, request, *args, **kwargs):
        return render(request, 'doortodoor/ajouter.html')

    def post(self, request, *args, **kwargs):
        """
        Formulaire qui permet d'ajouter des livraisons
        """ 
        libelle = request.POST.get('libelle')
        description = request.POST.get('description')
        #prix_article = request.POST.get('prix_article')
        nom_client = request.POST.get('nom_client')
        adresse_client = request.POST.get('adresse_client')
        contact_client = request.POST.get('contact_client')
        #Mettre le client qui a ajouter l'article
        list_id = []
        user_id= request.user.id
        list_id.append(user_id)

        article = Article.objects.create(
            libelle= libelle,
            description= description,
            #prix_article= prix_article,
            nom_client= nom_client,
            adresse_client= adresse_client,
            contact_client= contact_client,
        )
        article.user.add(*list_id)

        context = {
                'id': article.pk,
            }
        return redirect('confirmation-article', pk=article.pk)

    def test_func(self):
        return self.request.user.groups.filter(name='Clients')


class ConfirmationArticle(LoginRequiredMixin,UserPassesTestMixin,View):
    def get(self, request, pk, *args, **kwargs):
        article = Article.objects.get(pk=pk)
        context = {
            'pk': article.pk,
            'nom_client': article.nom_client,
            'contact_client': article.contact_client,
            'adresse': article.adresse_client,
            'user': request.user,
        }
        return render(request, 'doortodoor/confirmation-article.html', context)
        
    def post(self, request, pk, *args, **kwargs):
        print(request.body)

    def test_func(self):
        return self.request.user.groups.filter(name='Clients')



