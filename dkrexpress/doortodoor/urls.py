from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
#from customer.views import Index, About
from doortodoor.views import Index, About, AjouterLivraison, UpdateArticle, ModifierLivraison, DashboardJournalier, DashboardSearch, ListeRetourSearch, LivraisonDetails, ModifierStatut, ListeEnCours

urlpatterns = [
    path('', Index.as_view(), name = 'index'),
    path('about/', About.as_view(), name = 'about'),
    path('article/', AjouterLivraison.as_view(), name = 'ajouter'),
    path('update/<int:pk>', UpdateArticle.as_view(), name='update'),
    path('livraison/<int:pk>', ModifierLivraison.as_view(), name='ajout-livraison'),

    path('dailyDashboard/', DashboardJournalier.as_view(), name = 'dashboard-journalier'),
    path('dailyDashboard/search', DashboardJournalier.as_view(), name = 'dashboard-journalier-search'),
    path('dashboard/', DashboardSearch.as_view(), name = 'dashboard'),
    path('dashboard/search', DashboardSearch.as_view(), name = 'dashboard-search'),


    path('liste-retour/', ListeRetourSearch.as_view(), name='liste-retour'),
    path('retour/search', ListeRetourSearch.as_view(), name = 'retour-search'),
    path('details/<int:pk>', LivraisonDetails.as_view(), name='livraison-details'),
    path('modifier/<int:pk>', ModifierStatut.as_view(), name='modifier-livraison'),
    path('attente/', ListeEnCours.as_view(), name = 'liste-en-cours')



] 
urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
