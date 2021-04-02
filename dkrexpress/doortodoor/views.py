from django.shortcuts import render, redirect
# Create your views here.
from django.views import View
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.utils.timezone import datetime
from doortodoor.models import *
from django.db.models import Q
from django.conf import settings
from django.core.mail import send_mail
from .forms import *


class Index(LoginRequiredMixin,UserPassesTestMixin, View):
    def get(self,request, *args, **kwargs):
        if request.user.groups.filter(name='Admin') or request.user.groups.filter(name='Clients'):
            return render(request,'doortodoor/index.html')
        else:
            return redirect('dashboard')
    
    def test_func(self):
        return self.request.user.groups.all() #filter(name='Clients') 


class About(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'doortodoor/about.html')
    
    def test_func(self):
        return self.request.user.groups.all()


class AjouterLivraison(LoginRequiredMixin,UserPassesTestMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.groups.filter(name='Admin') or request.user.groups.filter(name='Clients'):
            form = ArticleForm()
            return render(request, 'doortodoor/ajouter.html', {'form': form})
        else:
            return redirect('dashboard')

    def post(self, request, *args, **kwargs):
        """
        Formulaire qui permet d'ajouter des livraisons par le client
        user autorisé: admin, client
        """ 
        libelle = request.POST.get('libelle')
        montant_livraison = request.POST.get('montant_livraison')
        prix_article = request.POST.get('prix_article')

        nom_client = request.POST.get('nom_client')
        adresse_client = request.POST.get('adresse_client')
        contact_client = request.POST.get('contact_client')
        #Mettre le client qui a ajouter l'article
        list_id = []
        user_id= request.user.id
        list_id.append(user_id)

        article = Article.objects.create(
            libelle= libelle,
            montant_livraison= montant_livraison,
            prix_article= prix_article,
            nom_client= nom_client,
            adresse_client= adresse_client,
            contact_client= contact_client,
        )

        article.user.add(*list_id)
        
        list_id_article = []
        list_id_article.append(article.pk)
        livraison = Livraison.objects.create()
        livraison.article.add(*list_id_article)
        livraison.user.add(*list_id)


        context = {
                'id': article.pk,
            }
        """
        si l'utilisateur save add another-> ajouter
        si l'utilisateur save -> dashboard
        """
        if "another" in request.POST:
            return redirect('ajouter')
            
        return redirect('dashboard')


    def test_func(self):
        return self.request.user.groups.all()


class UpdateArticle(LoginRequiredMixin, UserPassesTestMixin,View):
    """
    fonction qui permet de mopdifier ou supprimer un aticle
    prendre l'id de l'article et modifier enregistrer
    user autorisé: admin, client
    """

    def get(self, request, pk, *args, **kwargs):
        article = Article.objects.get(pk=pk)
        livraison = Livraison.objects.filter(article=article)
        statut = ''
        for liv in livraison:
            
            statut = liv.statut
        if request.user.groups.filter(name='Admin') or request.user.groups.filter(name='Clients'):
            if statut != "livré":
                form = ArticleForm(instance = article)
                return render(request, 'doortodoor/update-article.html', {'form': form})

        return redirect('dashboard')

    def post(self, request, pk, *args, **kwargs):
        # fetch the object related to passed id
        article = Article.objects.get(pk=pk)
        form = ArticleForm(request.POST or None,instance = article)
        # save the data from the form and
        # redirect to detail_view
        if 'update' in request.POST:
            if form.is_valid():
                article.date_ajout = datetime.now()
                form.save()
                article.save()
    
                livraison = Livraison.objects.get(article=article)
                livraison.statut = "en cours"
                user_id= request.user.id
                client = [user.username for user in User.objects.filter(livraison=livraison)]
                list_id = []
                list_id.append(user_id)
                livraison.user.clear()
                livraison.user.add(*list_id)
                livraison.date_statut = datetime.now()
                livraison.save()


        elif 'delete'in request.POST:
            livraison = Livraison.objects.get(article=article)
            livraison.delete()
            article.delete()

        return redirect('dashboard')

    def test_func(self):
        return self.request.user.groups.all()


class ModifierLivraison(LoginRequiredMixin,UserPassesTestMixin,View):
    """
    fonction qui permet de faire une livraison en ajoutant le prix 
    prendre l'id de la livraison et modifier le prix
    changer statut
    ajouter celui qui a modifier la livraison
    user autorisé: admin, livreur
    """

    def get(self, request,pk, *args, **kwargs):
        if request.user.groups.filter(name='Admin') or request.user.groups.filter(name='Livreurs'):
            livraison = Livraison.objects.get(pk=pk)
            context = {
                'id': livraison.pk,
                }

            return render(request, 'doortodoor/ajouter-livraison.html', context)
        else:
            return redirect('dashboard')
    
    def post(self, request, pk, *args, **kwargs):
        livraison = Livraison.objects.get(pk=pk)
        livraison.prix_livraison = request.POST.get('prix_livraison')
        livraison.statut = "livré"
        user_id= request.user.id
        client = [user.username for user in User.objects.filter(livraison=livraison)]
        list_id = []
        list_id.append(user_id)
        livraison.user.clear()
        livraison.user.add(*list_id)
        livraison.date_statut = datetime.now()

        livraison.save()
        #After everything is done, send confirmation mail to the user
        article_item = Article.objects.filter(article = livraison)
        article_added_by=[]
        libelle=''
        for article in article_item:
                article_added_by = [user.email for user in User.objects.filter(article=article)]
                libelle = article.libelle

        # body = (f'Bonjour {client[0]},\n'
        # f'Votre article a été livré avec succés par {request.user.username} \n'
        # f'Montant Livraison: {livraison.prix_livraison}\n'
        # 'Merci\n'
        # 'Door To Door Team!'
        # )
        # email_from=settings.EMAIL_HOST_USER
        # send_mail(
        #     f'Livraison {libelle}',
        #     body,
        #     email_from,
        #     article_added_by,
        #     fail_silently=False
        # )
        context = {
                'id': livraison.pk,
            }
        return redirect('livraison-details', pk=livraison.pk)

    def test_func(self):
        return self.request.user.groups.all() #filter(name='')


class LivraisonDetails(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request, pk, *args, **kwargs):
        livraison = Livraison.objects.get(pk=pk)
        livraison_modified_by = [user.username for user in User.objects.filter(livraison=livraison)]
        liv = {
            'livraison_list': []
        }
        ship_data ={

                'livraison_modified_by': livraison_modified_by[0],
                'statut': livraison.statut,
                'date_statut': livraison.date_statut,
                'prix_livraison': livraison.prix_livraison,
                'livraison_id': livraison.pk
                }
        #Append ship data
        liv['livraison_list'].append(ship_data)

        context={
            'livraison': liv['livraison_list']
        }

        return render(request, 'doortodoor/livraison-details.html', context)
    
    def test_func(self):
        return self.request.user.groups.all() #filter(name='Staff').exists()


class ModifierStatut(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Modifier lee statut de la livraison
    user autorisé: admin, livreur
    """

    def get(self, request, pk, *args, **kwargs):
        liv = {
                'livraison_list': []
            }

        if request.user.groups.filter(name='Admin') or request.user.groups.filter(name='Livreurs'):
            livraison = Livraison.objects.get(pk=pk)
            livraison_modified_by = [user.username for user in User.objects.filter(livraison=livraison)]
            ship_data ={
                    'livraison_modified_by': livraison_modified_by[0],
                    'statut': livraison.statut,
                    'date_statut': livraison.date_statut,
                    'livraison_id': livraison.pk
                    }

            #Append ship data
            liv['livraison_list'].append(ship_data)

            context={
                    'livraison': liv['livraison_list']
                }

            return render(request, 'doortodoor/modifier-statut.html', context)

        else:
            return redirect('dashboard')


    def post(self, request, pk, *args, **kwargs):
        livraison = Livraison.objects.get(pk=pk)
        user_id= request.user.id
        list_id = []
        list_id.append(user_id)
        livraison.user.clear()
        livraison.user.add(*list_id)

        if livraison.statut == "livré":
            livraison.statut = "retour"
            livraison.prix_livraison=0
        elif livraison.statut == "en cours":
            livraison.statut = "retour"
        else:
            livraison.statut = "en cours"
        livraison.date_statut = datetime.now()
        livraison.save()

        context = {
                'id': livraison.pk,
            }

        return redirect('dashboard')

    def test_func(self):
        return self.request.user.groups.all()


class Dashboard(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request, *args, **kwargs):
        """
        parcourir toutes les livraisons ajouter les elements au tableau de bord
        Calculer montant total
        Nombre de livraison total
        user autorisé: admin | client | livreur | Employe
        """
        today = datetime.today()
        livraison = Livraison.objects.filter(date_statut__year=today.year,
            date_statut__month=today.month,date_statut__day=today.day)
        ship = {
            'livraison_list': []
        }
        montant_article = 0
        montant_recu = 0
        nombre_livraison = 0
        user_id= request.user.id

        if request.user.groups.filter(name='Clients'):
            article = Article.objects.filter(date_ajout__year=today.year,
            date_ajout__month=today.month,date_ajout__day=today.day,user = user_id)
            for art in article:
                montant_article += art.prix_article + art.montant_livraison
                livraison = Livraison.objects.filter(article=art)
                for liv in livraison:
                    montant_recu +=liv.prix_livraison
                    livraison_modified_by = [user.username for user in User.objects.filter(livraison=liv)]
                    article_item = Article.objects.filter(article = liv)
                    article_added_by = [user.username for user in User.objects.filter(article=art)]
                    ship_data ={
                                'id_article': art.id,
                                'nom_client': art.nom_client,
                                'contact_client': art.contact_client,
                                'libelle_article': art.libelle,
                                'adresse_client': art.adresse_client,
                                'date_ajout': art.date_ajout,
                                'montant': art.prix_article + art.montant_livraison,
                                'article_added_by': article_added_by[0],
                                'livraison_modified_by': livraison_modified_by[0],
                                'statut': liv.statut,
                                'date_statut': liv.date_statut,
                                'prix_livraison': liv.prix_livraison,
                                'livraison_id': liv.pk
                                }
                        #Append ship data
                    ship['livraison_list'].append(ship_data)                    
                    nombre_livraison += 1

        else:
            for liv in livraison:
                livraison_modified_by = [user.username for user in User.objects.filter(livraison=liv)]
                if request.user.groups.filter(name='Livreurs'):
                    if livraison_modified_by[0]==request.user.username:
                        montant_recu +=liv.prix_livraison
                        nombre_livraison +=1
                else:
                    montant_recu +=liv.prix_livraison
                    nombre_livraison +=1
                article_item = Article.objects.filter(article = liv)
                for article in article_item:
                    montant_article += article.prix_article + article.montant_livraison
                    article_added_by = [user.username for user in User.objects.filter(article=article)]
                    ship_data ={
                                'id_article': article.id,
                                'nom_client': article.nom_client,
                                'contact_client': article.contact_client,
                                'libelle_article': article.libelle,
                                'adresse_client': article.adresse_client,
                                'date_ajout': article.date_ajout,
                                'montant': article.prix_article + article.montant_livraison,
                                'article_added_by': article_added_by[0],
                                'livraison_modified_by': livraison_modified_by[0],
                                'statut': liv.statut,
                                'date_statut': liv.date_statut,
                                'prix_livraison': liv.prix_livraison,
                                'livraison_id': liv.pk
                                }
                    #Append ship data
                    ship['livraison_list'].append(ship_data)

        ship['livraison_list'].sort(key=lambda item:item['date_ajout'], reverse=True)
        #Ajouter les données dans context
        context={
            'livraison': ship['livraison_list'],
            'montant_recu': montant_recu,
            'total_livraison': nombre_livraison,
            'montant_articles': montant_article,
        }

        return render(request,'doortodoor/dashboard.html', context)

    def test_func(self):
        return self.request.user.groups.all()


class DashboardSearch(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request, *args, **kwargs):
        query = self.request.GET.get("q")
        today = datetime.today()
        query_date_filter = datetime.today()
        query_date_filter = datetime.strptime(query, "%Y-%m-%d")
        livraison = Livraison.objects.filter(Q(date_statut__icontains=query))
        ship = {
            'livraison_list': []
        }
        montant_article = 0
        montant_recu = 0
        nombre_livraison = 0
        user_id= request.user.id

        if request.user.groups.filter(name='Admin') or request.user.groups.filter(name='Employes'):
            for liv in livraison:
                montant_recu +=liv.prix_livraison
                livraison_modified_by = [user.username for user in User.objects.filter(livraison=liv)]
                article_item = Article.objects.filter(article = liv)
                for article in article_item:
                    montant_article += article.prix_article + article.montant_livraison
                    article_added_by = [user.username for user in User.objects.filter(article=article)]
                    ship_data ={
                                'id_article': article.id,
                                'nom_client': article.nom_client,
                                'contact_client': article.contact_client,
                                'libelle_article': article.libelle,
                                'adresse_client': article.adresse_client,
                                'date_ajout': article.date_ajout,
                                'montant': article.prix_article + article.montant_livraison,
                                'article_added_by': article_added_by[0],
                                'livraison_modified_by': livraison_modified_by[0],
                                'statut': liv.statut,
                                'date_statut': liv.date_statut,
                                'prix_livraison': liv.prix_livraison,
                                'livraison_id': liv.pk
                                }
                    #Append ship data
                    ship['livraison_list'].append(ship_data)
                    nombre_livraison += 1

        elif request.user.groups.filter(name='Clients'):
            article = Article.objects.filter(user = user_id, date_ajout__year=query_date_filter.year,
            date_ajout__month=query_date_filter.month, date_ajout__day=query_date_filter.day)
            for art in article:
                montant_article += art.prix_article + art.montant_livraison
                livraison = Livraison.objects.filter(article=art)
                for liv in livraison:
                    montant_recu +=liv.prix_livraison
                    livraison_modified_by = [user.username for user in User.objects.filter(livraison=liv)]
                    article_item = Article.objects.filter(article = liv)
                    article_added_by = [user.username for user in User.objects.filter(article=art)]
                    ship_data ={
                                'id_article': art.id,
                                'nom_client': art.nom_client,
                                'contact_client': art.contact_client,
                                'libelle_article': art.libelle,
                                'adresse_client': art.adresse_client,
                                'date_ajout': art.date_ajout,
                                'montant': art.prix_article + art.montant_livraison,
                                'article_added_by': article_added_by[0],
                                'livraison_modified_by': livraison_modified_by[0],
                                'statut': liv.statut,
                                'date_statut': liv.date_statut,
                                'prix_livraison': liv.prix_livraison,
                                'livraison_id': liv.pk
                                }
                        #Append ship data
                    ship['livraison_list'].append(ship_data)                    
                    nombre_livraison += 1

        ship['livraison_list'].sort(key=lambda item:item['date_ajout'], reverse=True)
        #Ajouter les données dans context
        context={
            'livraison': ship['livraison_list'],
            'montant_recu': montant_recu,
            'total_livraison': nombre_livraison,
            'montant_articles': montant_article,
        }
        
        return render(request,'doortodoor/dashboard.html', context)

    def test_func(self):
        return self.request.user.groups.all()


class ListeRetour(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request, *args, **kwargs):
        """
        parcourir toutes les livraisons ajouter les elements au tableau de bord
        Calculer montant total
        Nombre de livraison total
        user autorisé: admin | client | livreur
        """
        today = datetime.today()
        livraison = Livraison.objects.filter(statut='retour',date_statut__month=today.month)
        ship = {
            'livraison_list': []
        }
        nombre_livraison = 0
        user_id= request.user.id

        if request.user.groups.filter(name='Admin') or request.user.groups.filter(name='Employes'):
            for liv in livraison:
                livraison_modified_by = [user.username for user in User.objects.filter(livraison=liv)]
                article_item = Article.objects.filter(article = liv)
                for article in article_item:
                    article_added_by = [user.username for user in User.objects.filter(article=article)]
                    ship_data ={
                                'id_article': article.id,
                                'nom_client': article.nom_client,
                                'libelle_article': article.libelle,
                                'adresse_client': article.adresse_client,
                                'contact_client': article.contact_client,
                                'date_ajout': article.date_ajout,
                                'article_added_by': article_added_by[0],
                                'livraison_modified_by': livraison_modified_by[0],
                                'statut': liv.statut,
                                'date_statut': liv.date_statut,
                                'livraison_id': liv.pk
                                }
                    #Append ship data
                    ship['livraison_list'].append(ship_data)
                    nombre_livraison += 1

        elif request.user.groups.filter(name='Clients'):
            article = Article.objects.filter(date_ajout__month=today.month,user=user_id)
            for art in article:
                livraison = Livraison.objects.filter(article=art, statut='retour')
                for liv in livraison:
                    livraison_modified_by = [user.username for user in User.objects.filter(livraison=liv)]
                    article_item = Article.objects.filter(article = liv)
                    article_added_by = [user.username for user in User.objects.filter(article=art)]
                    ship_data ={
                                'id_article': art.id,
                                'nom_client': art.nom_client,
                                'libelle_article': art.libelle,
                                'adresse_client': art.adresse_client,
                                'contact_client': art.contact_client,
                                'date_ajout': art.date_ajout,
                                'article_added_by': article_added_by[0],
                                'livraison_modified_by': livraison_modified_by[0],
                                'statut': liv.statut,
                                'date_statut': liv.date_statut,
                                'livraison_id': liv.pk
                                }
                        #Append ship data
                    ship['livraison_list'].append(ship_data)                    
                    nombre_livraison += 1

        elif request.user.groups.filter(name='Livreurs'):
            livraison = Livraison.objects.filter(user = user_id,statut='retour',date_statut__month=today.month)
            for liv in livraison:
                livraison_modified_by = [user.username for user in User.objects.filter(livraison=liv)]
                article_item = Article.objects.filter(article = liv)
                for article in article_item:
                    article_added_by = [user.username for user in User.objects.filter(article=article)]
                    ship_data ={
                                'id_article': article.id,
                                'nom_client': article.nom_client,
                                'libelle_article': article.libelle,
                                'adresse_client': article.adresse_client,
                                'contact_client': article.contact_client,
                                'date_ajout': article.date_ajout,
                                'article_added_by': article_added_by[0],
                                'livraison_modified_by': livraison_modified_by[0],
                                'statut': liv.statut,
                                'date_statut': liv.date_statut,
                                'livraison_id': liv.pk
                                }
                    #Append ship data
                    ship['livraison_list'].append(ship_data)
                    nombre_livraison += 1
            
        #Ajouter les données dans context
        context={
            'livraison': ship['livraison_list'],
            'total_livraison': nombre_livraison,
        }

        return render(request,'doortodoor/liste-retour.html', context)

    def test_func(self):
        return self.request.user.groups.all()



class ListeRetourSearch(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request, *args, **kwargs):
        """
        parcourir toutes les livraisons ajouter les elements au tableau de bord
        Calculer montant total
        Nombre de livraison total
        user autorisé: admin | client | livreur
        """
        query = self.request.GET.get("q")
        today = datetime.today()
        query_date_filter = datetime.today()
        query_date_filter = datetime.strptime(query, "%Y-%m")
        livraison = Livraison.objects.filter(Q(created_on__icontains=query),statut='retour')
        ship = {
            'livraison_list': []
        }
        nombre_livraison = 0
        user_id= request.user.id

        if request.user.groups.filter(name='Admin') or request.user.groups.filter(name='Employes'):
            for liv in livraison:
                livraison_modified_by = [user.username for user in User.objects.filter(livraison=liv)]
                article_item = Article.objects.filter(article = liv)
                for article in article_item:
                    article_added_by = [user.username for user in User.objects.filter(article=article)]
                    ship_data ={
                                'id_article': article.id,
                                'nom_client': article.nom_client,
                                'libelle_article': article.libelle,
                                'adresse_client': article.adresse_client,
                                'contact_client': article.contact_client,
                                'date_ajout': article.date_ajout,
                                'article_added_by': article_added_by[0],
                                'livraison_modified_by': livraison_modified_by[0],
                                'statut': liv.statut,
                                'date_statut': liv.date_statut,
                                'livraison_id': liv.pk
                                }
                    #Append ship data
                    ship['livraison_list'].append(ship_data)
                    nombre_livraison += 1

                    

        elif request.user.groups.filter(name='Clients'):
            article = Article.objects.filter(user = user_id)
            for art in article:
                livraison = Livraison.objects.filter(Q(created_on__icontains=query),article=art, statut='retour')
                for liv in livraison:
                    livraison_modified_by = [user.username for user in User.objects.filter(livraison=liv)]
                    article_item = Article.objects.filter(article = liv)
                    article_added_by = [user.username for user in User.objects.filter(article=art)]
                    ship_data ={
                                'id_article': art.id,
                                'nom_client': art.nom_client,
                                'libelle_article': art.libelle,
                                'adresse_client': art.adresse_client,
                                'contact_client': art.contact_client,
                                'date_ajout': art.date_ajout,
                                'article_added_by': article_added_by[0],
                                'livraison_modified_by': livraison_modified_by[0],
                                'statut': liv.statut,
                                'date_statut': liv.date_statut,
                                'livraison_id': liv.pk
                                }
                        #Append ship data
                    ship['livraison_list'].append(ship_data)                    
                    nombre_livraison += 1

        elif request.user.groups.filter(name='Livreurs'):
            livraison = Livraison.objects.filter(Q(created_on__icontains=query),user = user_id,statut='retour')
            for liv in livraison:
                livraison_modified_by = [user.username for user in User.objects.filter(livraison=liv)]
                article_item = Article.objects.filter(article = liv)
                for article in article_item:
                    article_added_by = [user.username for user in User.objects.filter(article=article)]
                    ship_data ={
                                'id_article': article.id,
                                'nom_client': article.nom_client,
                                'libelle_article': article.libelle,
                                'adresse_client': article.adresse_client,
                                'contact_client': article.contact_client,
                                'date_ajout': article.date_ajout,
                                'article_added_by': article_added_by[0],
                                'livraison_modified_by': livraison_modified_by[0],
                                'statut': liv.statut,
                                'date_statut': liv.date_statut,
                                'livraison_id': liv.pk
                                }
                    #Append ship data
                    ship['livraison_list'].append(ship_data)
                    nombre_livraison += 1
            
        #Ajouter les données dans context
        context={
            'livraison': ship['livraison_list'],
            'total_livraison': nombre_livraison,
        }

        return render(request,'doortodoor/liste-retour.html', context)

    def test_func(self):
        return self.request.user.groups.all()