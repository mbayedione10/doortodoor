from django import forms
from .models import *

# creating a form
class ArticleForm(forms.ModelForm):
  
    # create meta class
    class Meta:
        # specify model to be used
        model = Article
  
        # specify fields to be used
        fields = [
            "libelle",
            "prix_article",
            "montant_livraison",
            "nom_client",
            "adresse_client",
            "contact_client"
            ]