from django.urls import path
from django.conf.urls import url, include
from django.contrib import admin
#from customer.views import Index, About
from doortodoor.views import *

urlpatterns = [
    path('', Index.as_view(), name = 'index'),
    path('about/', About.as_view(), name = 'about'),
    path('article/', AjouterLivraison.as_view(), name = 'ajouter'),
    path('confirmation-article/<int:pk>', ConfirmationArticle.as_view(), name='confirmation-article'),
    path('livraison/<int:pk>', ModifierLivraison.as_view(), name='ajout-livraison'),
    path('dashboard/', Dashboard.as_view(), name = 'dashboard'),
    path('dashboard/search', DashboardSearch.as_view(), name = 'dashboard-search'),
    path('details/<int:pk>', LivraisonDetails.as_view(), name='livraison-details'),
    path('modifier/<int:pk>', ModifierStatut.as_view(), name='modifier-livraison'),
 
    

]   