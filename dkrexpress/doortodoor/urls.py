from django.urls import path
from django.conf.urls import url, include
from django.contrib import admin
#from customer.views import Index, About
from doortodoor.views import *

urlpatterns = [
    path('', Index.as_view(), name = 'index'),
    path('about/', About.as_view(), name = 'about'),
    path('article/', AjouterArticle.as_view(), name = 'ajouter'),
    path('confirmation-article/<int:pk>', ConfirmationArticle.as_view(), name='confirmation-article'),
    path('livraison/',AjouterLivraison.as_view(), name='ajout-livraison'),

]