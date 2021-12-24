from django.db import models
from django.contrib.auth.models import User

# Create your models here.

EN_COURS = 'en cours'
LIVRE = 'livré'
RETOUR = 'retour'

STATUS_TYPES = (
    (EN_COURS, EN_COURS),
    (LIVRE, LIVRE),
    (RETOUR, RETOUR),
)


class Article(models.Model):
    libelle = models.CharField(max_length=100)
    # description =  models.TextField(blank=True)
    prix_article = models.IntegerField(blank=True)
    montant_livraison = models.IntegerField(blank=True)
    user = models.ManyToManyField(User)
    # Information du client
    nom_client = models.CharField(max_length=100)
    adresse_client = models.CharField(max_length=150, null=False)
    contact_client = models.PositiveIntegerField(null=False)
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Article: {self.libelle}'
        # date_ajout.strftime("%b %d %Y %I:%M %p")


class Livraison(models.Model):
    article = models.ManyToManyField('Article', related_name='article')
    user = models.ManyToManyField(User)
    statut = models.CharField(max_length=20, choices=STATUS_TYPES, blank=False, null=False, default=EN_COURS)
    date_statut = models.DateTimeField(auto_now_add=True)
    prix_livraison = models.IntegerField(default=0, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Livraison : {self.statut}'
        # date_statut.strftime("%b %d %Y %I:%M %p")}'
