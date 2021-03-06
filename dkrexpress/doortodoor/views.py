from django.shortcuts import render, redirect
# Create your views here.
from django.views import View
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.utils.timezone import datetime
from doortodoor.models import Article, Livraison, User
from django.db.models import Q
from django.conf import settings
from django.core.mail import send_mail
from .forms import ArticleForm


class Index(LoginRequiredMixin, UserPassesTestMixin, View):
    @staticmethod
    def get(request, *args, **kwargs):
        if request.user.groups.filter(name='Admin') or request.user.groups.filter(name='Clients'):
            return render(request, 'doortodoor/index.html')
        return redirect('dashboard')

    def test_func(self):
        return self.request.user.groups.all()


class About(View):
    @staticmethod
    def get(request, *args, **kwargs):
        return render(request, 'doortodoor/about.html')


class AjouterLivraison(LoginRequiredMixin, UserPassesTestMixin, View):
    @staticmethod
    def get(request, *args, **kwargs):
        if request.user.groups.filter(name='Admin') or request.user.groups.filter(name='Clients'):
            form = ArticleForm()
            return render(request, 'doortodoor/ajouter.html', {'form': form})
        return redirect('dashboard')

    @staticmethod
    def post(request, *args, **kwargs):
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
        user_id = request.user.id
        list_id.append(user_id)

        article = Article.objects.create(
            libelle=libelle,
            montant_livraison=montant_livraison,
            prix_article=prix_article,
            nom_client=nom_client,
            adresse_client=adresse_client,
            contact_client=contact_client,
        )

        article.user.add(*list_id)

        list_id_article = []
        list_id_article.append(article.pk)
        livraison = Livraison.objects.create()
        livraison.article.add(*list_id_article)
        livraison.user.add(*list_id)
        """
        si l'utilisateur save add another-> ajouter
        si l'utilisateur save -> dashboard
        """
        if "another" in request.POST:
            return redirect('ajouter')

        return redirect('dashboard')

    def test_func(self):
        return self.request.user.groups.all()


class UpdateArticle(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    fonction qui permet de mopdifier ou supprimer un aticle
    prendre l'id de l'article et modifier enregistrer
    user autorisé: admin, client
    """

    @staticmethod
    def get(request, pk, *args, **kwargs):
        article = Article.objects.get(pk=pk)
        livraison = Livraison.objects.filter(article=article)
        statut = ''
        for liv in livraison:
            statut = liv.statut
        if (request.user.groups.filter(name='Admin') or request.user.groups.filter(
                name='Clients')) and statut != "livré":
            form = ArticleForm(instance=article)
            return render(request, 'doortodoor/update-article.html', {'form': form})

        return redirect('dashboard')

    @staticmethod
    def post(request, pk, *args, **kwargs):
        # fetch the object related to passed id
        article = Article.objects.get(pk=pk)
        form = ArticleForm(request.POST or None, instance=article)
        # save the data from the form and
        # redirect to detail_view
        if 'update' in request.POST and form.is_valid():
            article.date_ajout = datetime.now()
            form.save()
            article.save()
            livraison = Livraison.objects.get(article=article)
            livraison.statut = "en cours"
            user_id = request.user.id
            list_id = []
            list_id.append(user_id)
            livraison.user.clear()
            livraison.user.add(*list_id)
            livraison.date_statut = datetime.now()
            livraison.save()


        elif 'delete' in request.POST and request.user.groups.filter(name='Admin'):
            livraison = Livraison.objects.get(article=article)
            livraison.delete()
            article.delete()

        return redirect('dashboard')

    def test_func(self):
        return self.request.user.groups.all()


class ModifierLivraison(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    fonction qui permet de faire une livraison en ajoutant le prix 
    prendre l'id de la livraison et modifier le prix
    changer statut
    ajouter celui qui a modifier la livraison
    user autorisé: admin, livreur
    """

    @staticmethod
    def get(request, pk, *args, **kwargs):
        if request.user.groups.filter(name='Admin') or request.user.groups.filter(name='Livreurs'):
            livraison = Livraison.objects.get(pk=pk)

            article = Article.objects.filter(article=livraison)
            for art in article:
                form1 = ArticleForm(instance=art)
            context = {
                'id': livraison.pk,
                'form1': form1,
            }

            return render(request, 'doortodoor/ajouter-livraison.html', context)
        return redirect('dashboard')

    @staticmethod
    def post(request, pk, *args, **kwargs):
        livraison = Livraison.objects.get(pk=pk)
        livraison.prix_livraison = request.POST.get('prix_livraison')
        livraison.statut = "livré"
        user_id = request.user.id
        list_id = []
        list_id.append(user_id)
        livraison.user.clear()
        livraison.user.add(*list_id)
        livraison.date_statut = datetime.now()

        livraison.save()
        return redirect('dashboard')

    def test_func(self):
        return self.request.user.groups.all()


class LivraisonDetails(LoginRequiredMixin, UserPassesTestMixin, View):
    @staticmethod
    def get(request, pk, *args, **kwargs):
        livraison = Livraison.objects.get(pk=pk)
        livraison_modified_by = [user.username for user in User.objects.filter(livraison=livraison)]
        liv = []
        ship_data = {
            'livraison_modified_by': livraison_modified_by[0],
            'statut': livraison.statut,
            'date_statut': livraison.date_statut,
            'prix_livraison': livraison.prix_livraison,
            'livraison_id': livraison.pk
        }
        # Append ship data
        liv.append(ship_data)

        context = {
            'livraison': liv
        }

        return render(request, 'doortodoor/livraison-details.html', context)

    def test_func(self):
        return self.request.user.groups.all()


class ModifierStatut(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Modifier lee statut de la livraison
    user autorisé: admin, livreur
    """

    @staticmethod
    def get(request, pk, *args, **kwargs):
        liv = []
        if request.user.groups.filter(name='Admin') or request.user.groups.filter(name='Livreurs'):
            livraison = Livraison.objects.get(pk=pk)
            livraison_modified_by = [user.username for user in User.objects.filter(livraison=livraison)]
            ship_data = {
                'livraison_modified_by': livraison_modified_by[0],
                'statut': livraison.statut,
                'date_statut': livraison.date_statut,
                'livraison_id': livraison.pk
            }

            # Append ship data
            liv.append(ship_data)

            context = {
                'livraison': liv
            }

            return render(request, 'doortodoor/modifier-statut.html', context)
        return redirect('dashboard')

    @staticmethod
    def post(request, pk, *args, **kwargs):
        livraison = Livraison.objects.get(pk=pk)
        user_id = request.user.id
        list_id = []
        list_id.append(user_id)
        livraison.user.clear()
        livraison.user.add(*list_id)

        if livraison.statut == "livré":
            livraison.statut = "retour"
            livraison.prix_livraison = 0
        elif livraison.statut == "en cours":
            livraison.statut = "retour"
        else:
            livraison.statut = "en cours"
        livraison.date_statut = datetime.now()
        livraison.save()

        return redirect('dashboard')

    def test_func(self):
        return self.request.user.groups.all()


class DashboardJournalier(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request, *args, **kwargs):
        query = self.request.GET.get("q")
        today = datetime.today()

        if query is None:
            livraison = Livraison.objects.filter(created_on__year=today.year,
                                                 created_on__month=today.month, created_on__day=today.day)
        else:
            query_date_filter = datetime.strptime(query, "%Y-%m-%d")
            livraison = Livraison.objects.filter(
                Q(created_on__year=query_date_filter.year) &
                Q(created_on__month=query_date_filter.month) &
                Q(created_on__day=query_date_filter.day))

        ship = []
        montant_article = 0
        montant_recu = 0
        nombre_livraison = 0
        user_id = request.user.id

        if request.user.groups.filter(name='Clients'):
            if query is None:
                article = Article.objects.filter(user=user_id, date_ajout__year=today.year,
                                                 date_ajout__month=today.month, date_ajout__day=today.day)
            else:
                article = Article.objects.filter(user=user_id, date_ajout__year=query_date_filter.year,
                                                 date_ajout__month=query_date_filter.month,
                                                 date_ajout__day=query_date_filter.day)
            for art in article:
                livraison = Livraison.objects.filter(article=art)
                for liv in livraison:
                    montant_recu += liv.prix_livraison
                    article_item = Article.objects.filter(article=liv)
                    article_added_by = [user.username for user in User.objects.filter(article=art)]
                    ship_data = {
                        'id_article': art.id,
                        'nom_client': art.nom_client,
                        'contact_client': art.contact_client,
                        'libelle_article': art.libelle,
                        'adresse_client': art.adresse_client,
                        'montant': art.prix_article + art.montant_livraison,
                        'article_added_by': article_added_by[0],
                        'statut': liv.statut,
                        'date_created': liv.created_on,
                        'prix_livraison': liv.prix_livraison,
                        'livraison_id': liv.pk
                    }
                    montant_article += ship_data['montant']
                    # Append ship data
                    ship.append(ship_data)
                    if liv.statut == "livré":
                        nombre_livraison += 1

        else:
            for liv in livraison:
                livraison_modified_by = [user.username for user in User.objects.filter(livraison=liv)]
                if request.user.groups.filter(name='Livreurs'):
                    if livraison_modified_by[0] == request.user.username and liv.statut == "livré":
                            montant_recu +=liv.prix_livraison
                            nombre_livraison +=1
                else:
                    if liv.statut == "livré":
                        montant_recu += liv.prix_livraison
                        nombre_livraison += 1
                article_item = Article.objects.filter(article=liv)
                for article in article_item:
                    article_added_by = [user.username for user in User.objects.filter(article=article)]
                    ship_data = {
                        'id_article': article.id,
                        'nom_client': article.nom_client,
                        'contact_client': article.contact_client,
                        'libelle_article': article.libelle,
                        'adresse_client': article.adresse_client,
                        'prix_art': article.prix_article,
                        'prix_liv': article.montant_livraison,
                        'montant': article.prix_article + article.montant_livraison,
                        'article_added_by': article_added_by[0],
                        'statut': liv.statut,
                        'date_created': liv.created_on,
                        'prix_livraison': liv.prix_livraison,
                        'livraison_id': liv.pk
                    }
                    montant_article += ship_data['montant']
                    # Append ship data
                    ship.append(ship_data)
        ship.sort(key=lambda item: item['date_created'], reverse=True)
        # Ajouter les données dans context
        context = {
            'livraison': ship,
            'montant_recu': montant_recu,
            'total_livraison': nombre_livraison,
            'montant_articles': montant_article,
        }

        return render(request, 'doortodoor/dashboardJournalier.html', context)

    def test_func(self):
        return self.request.user.groups.all()


class DashboardSearch(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request, *args, **kwargs):
        query = self.request.GET.get("q")
        today = datetime.today()

        if query is None:
            livraison = Livraison.objects.filter(created_on__year=today.year,
                                                 created_on__month=today.month)
        else:
            query_date_filter = datetime.strptime(query, "%Y-%m")
            livraison = Livraison.objects.filter(
                Q(created_on__year=query_date_filter.year) &
                Q(created_on__month=query_date_filter.month))

        ship = []
        montant_article = 0
        montant_recu = 0
        nombre_livraison = 0
        user_id = request.user.id

        if request.user.groups.filter(name='Clients'):
            if query is None:
                article = Article.objects.filter(user=user_id, date_ajout__year=today.year,
                                                 date_ajout__month=today.month)
            else:
                article = Article.objects.filter(user=user_id, date_ajout__year=query_date_filter.year,
                                                 date_ajout__month=query_date_filter.month)
            for art in article:
                livraison = Livraison.objects.filter(article=art)
                for liv in livraison:
                    montant_recu += liv.prix_livraison
                    article_item = Article.objects.filter(article=liv)
                    article_added_by = [user.username for user in User.objects.filter(article=art)]
                    ship_data = {
                        'id_article': art.id,
                        'nom_client': art.nom_client,
                        'contact_client': art.contact_client,
                        'libelle_article': art.libelle,
                        'adresse_client': art.adresse_client,
                        'montant': art.prix_article + art.montant_livraison,
                        'article_added_by': article_added_by[0],
                        'statut': liv.statut,
                        'date_created': liv.created_on,
                        'prix_livraison': liv.prix_livraison,
                        'livraison_id': liv.pk
                    }
                    montant_article += ship_data['montant']
                    # Append ship data
                    ship.append(ship_data)
                    if liv.statut == "livré":
                        nombre_livraison += 1

        if request.user.groups.filter(name="Admin") or request.user.groups.filter(name="Employes"):
            for liv in livraison:
                article_item = Article.objects.filter(article=liv)
                montant_recu += liv.prix_livraison
                if liv.statut == "livré":
                    nombre_livraison +=1
                for article in article_item:
                    article_added_by = [user.username for user in User.objects.filter(article=article)]
                    ship_data = {
                        'id_article': article.id,
                        'nom_client': article.nom_client,
                        'contact_client': article.contact_client,
                        'libelle_article': article.libelle,
                        'adresse_client': article.adresse_client,
                        'prix_art': article.prix_article,
                        'prix_liv': article.montant_livraison,
                        'montant': article.prix_article + article.montant_livraison,
                        'article_added_by': article_added_by[0],
                        'statut': liv.statut,
                        'date_created': liv.created_on,
                        'prix_livraison': liv.prix_livraison,
                        'livraison_id': liv.pk
                    }
                    montant_article += ship_data['montant']
                    # Append ship data
                    ship.append(ship_data)
        if request.user.groups.filter(name='Livreurs'):
            if query is None:
                livraison = Livraison.objects.filter(created_on__month=today.month, user=user_id, statut='livré')
            else:
                livraison = Livraison.objects.filter(Q(created_on__icontains=query), user=user_id, statut='livré')
            for liv in livraison:
                montant_recu += liv.prix_livraison
                nombre_livraison +=1
                article_item = Article.objects.filter(article=liv)
                for article in article_item:
                    article_added_by = [user.username for user in User.objects.filter(article=article)]
                    ship_data = {
                        'id_article': article.id,
                        'nom_client': article.nom_client,
                        'contact_client': article.contact_client,
                        'libelle_article': article.libelle,
                        'adresse_client': article.adresse_client,
                        'prix_art': article.prix_article,
                        'prix_liv': article.montant_livraison,
                        'montant': article.prix_article + article.montant_livraison,
                        'article_added_by': article_added_by[0],
                        'statut': liv.statut,
                        'date_created': liv.created_on,
                        'prix_livraison': liv.prix_livraison,
                        'livraison_id': liv.pk
                    }
                    montant_article += ship_data['montant']
                    # Append ship data
                    ship.append(ship_data)
        ship.sort(key=lambda item: item['date_created'], reverse=True)
        # Ajouter les données dans context
        context = {
            'livraison': ship,
            'montant_recu': montant_recu,
            'total_livraison': nombre_livraison,
            'montant_articles': montant_article,
        }

        return render(request, 'doortodoor/dashboard.html', context)

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
        if query is None:
            today = datetime.today()
            livraison = Livraison.objects.filter(statut='retour', created_on__month=today.month)
        else:
            livraison = Livraison.objects.filter(Q(created_on__icontains=query), statut='retour')
        ship = []
        nombre_livraison = 0
        user_id = request.user.id

        if request.user.groups.filter(name='Admin') or request.user.groups.filter(name='Employes'):
            for liv in livraison:
                livraison_modified_by = [user.username for user in User.objects.filter(livraison=liv)]
                article_item = Article.objects.filter(article=liv)
                for article in article_item:
                    article_added_by = [user.username for user in User.objects.filter(article=article)]
                    ship_data = {
                        'id_article': article.id,
                        'nom_client': article.nom_client,
                        'libelle_article': article.libelle,
                        'contact_client': article.contact_client,
                        'date_ajout': article.date_ajout,
                        'article_added_by': article_added_by[0],
                        'livraison_modified_by': livraison_modified_by[0],
                        'statut': liv.statut,
                        'livraison_id': liv.pk
                    }
                    # Append ship data
                    ship.append(ship_data)
                    nombre_livraison += 1

        elif request.user.groups.filter(name='Clients'):
            article = Article.objects.filter(user=user_id)
            for art in article:
                if query is None:
                    livraison = Livraison.objects.filter(created_on__month=today.month, article=art, statut='retour')
                else:
                    livraison = Livraison.objects.filter(Q(created_on__icontains=query), article=art, statut='retour')
                for liv in livraison:
                    livraison_modified_by = [user.username for user in User.objects.filter(livraison=liv)]
                    article_item = Article.objects.filter(article=liv)
                    article_added_by = [user.username for user in User.objects.filter(article=art)]
                    ship_data = {
                        'id_article': art.id,
                        'nom_client': art.nom_client,
                        'libelle_article': art.libelle,
                        'contact_client': art.contact_client,
                        'date_ajout': art.date_ajout,
                        'article_added_by': article_added_by[0],
                        'livraison_modified_by': livraison_modified_by[0],
                        'statut': liv.statut,
                        'livraison_id': liv.pk
                    }
                    # Append ship data
                    ship.append(ship_data)
                    nombre_livraison += 1

        elif request.user.groups.filter(name='Livreurs'):
            if query is None:
                livraison = Livraison.objects.filter(created_on__month=today.month, user=user_id, statut='retour')
            else:
                livraison = Livraison.objects.filter(Q(created_on__icontains=query), user=user_id, statut='retour')
            for liv in livraison:
                livraison_modified_by = [user.username for user in User.objects.filter(livraison=liv)]
                article_item = Article.objects.filter(article=liv)
                for article in article_item:
                    article_added_by = [user.username for user in User.objects.filter(article=article)]
                    ship_data = {
                        'id_article': article.id,
                        'nom_client': article.nom_client,
                        'libelle_article': article.libelle,
                        'contact_client': article.contact_client,
                        'date_ajout': article.date_ajout,
                        'article_added_by': article_added_by[0],
                        'livraison_modified_by': livraison_modified_by[0],
                        'statut': liv.statut,
                        'livraison_id': liv.pk
                    }
                    # Append ship data
                    ship.append(ship_data)
                    nombre_livraison += 1

        # Ajouter les données dans context
        context = {
            'livraison': ship,
            'total_livraison': nombre_livraison,
        }

        return render(request, 'doortodoor/liste-retour.html', context)

    def test_func(self):
        return self.request.user.groups.all()


class ListeEnCours(LoginRequiredMixin, UserPassesTestMixin, View):
    @staticmethod
    def get(request, *args, **kargs):
        """
        parcourir toutes les livraisons en cours ajouter les elements au tableau de bord
        Calculer montant total
        user autorisé: admin | client | livreur
        """
        livraison = Livraison.objects.filter(statut='en cours')
        ship = []
        montant_article = 0
        nombre_livraison = 0
        user_id = request.user.id

        if request.user.groups.filter(name='Clients'):
            article = Article.objects.filter(user=user_id)
            for art in article:
                livraison = Livraison.objects.filter(article=art, statut='en cours')
                for liv in livraison:
                    article_item = Article.objects.filter(article=liv)
                    article_added_by = [user.username for user in User.objects.filter(article=art)]
                    ship_data = {
                        'id_article': art.id,
                        'nom_client': art.nom_client,
                        'contact_client': art.contact_client,
                        'libelle_article': art.libelle,
                        'adresse_client': art.adresse_client,
                        'montant': art.prix_article + art.montant_livraison,
                        'article_added_by': article_added_by[0],
                        'statut': liv.statut,
                        'date_created': liv.created_on,
                        'prix_livraison': liv.prix_livraison,
                        'livraison_id': liv.pk
                    }
                    montant_article += ship_data['montant']
                    nombre_livraison += 1
                    # Append ship data
                    ship.append(ship_data)
        else:
            for liv in livraison:
                article_item = Article.objects.filter(article=liv)
                for article in article_item:
                    article_added_by = [user.username for user in User.objects.filter(article=article)]
                    ship_data = {
                        'id_article': article.id,
                        'nom_client': article.nom_client,
                        'contact_client': article.contact_client,
                        'libelle_article': article.libelle,
                        'adresse_client': article.adresse_client,
                        'prix_art': article.prix_article,
                        'prix_liv': article.montant_livraison,
                        'montant': article.prix_article + article.montant_livraison,
                        'article_added_by': article_added_by[0],
                        'statut': liv.statut,
                        'date_created': liv.created_on,
                        'prix_livraison': liv.prix_livraison,
                        'livraison_id': liv.pk
                    }
                    montant_article += ship_data['montant']
                    nombre_livraison += 1
                    ship.append(ship_data)
        ship.sort(key=lambda item: item['date_created'], reverse=True)
        # Ajouter les données dans context
        context = {
            'livraison': ship,
            'montant_articles': montant_article,
            'total_livraison': nombre_livraison,
        }
        return render(request, 'doortodoor/dashboardEnCours.html', context)

    def test_func(self):
        return self.request.user.groups.all()
