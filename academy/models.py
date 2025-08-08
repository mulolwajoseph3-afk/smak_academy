from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import AbstractUser
from decimal import Decimal

# 🔐 Définition des rôles
ROLE_CHOICES = [
    ('superadmin', 'Super Administrateur'),
    ('promo', 'Admin École'),
    ('comptable', 'Comptable'),
]

# 🏫 École
class Ecole(models.Model):
    nom = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)  # ✅ Ajout du logo

    def __str__(self):
        return self.nom

# 👤 Utilisateur personnalisé
class User(AbstractUser):
    email = models.EmailField(unique=True, blank=True, null=True)
    nom_complet = models.CharField(max_length=200)
    telephone = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='comptable')
    ecole = models.ForeignKey(Ecole, on_delete=models.SET_NULL, null=True, blank=True)

    USERNAME_FIELD = 'username'  # 🔑 Crucial pour l'authentification

    def __str__(self):
        return self.username

    groups = models.ManyToManyField('auth.Group', related_name='academy_user_set', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='academy_user_permissions_set', blank=True)
    
# 📆 Année scolaire
from decimal import Decimal
from django.db import models

class AnneeScolaire(models.Model):
    nom_annee = models.CharField(max_length=10)
    ecole = models.ForeignKey('Ecole', on_delete=models.CASCADE, default=1)
    active = models.BooleanField(default=True)

    total_revenu = models.DecimalField(max_digits=15, decimal_places=2, default=0, blank=True, null=True)
    total_revenu_usd = models.DecimalField(max_digits=15, decimal_places=2, default=0, blank=True, null=True)
    total_depenses = models.DecimalField(max_digits=15, decimal_places=2, default=0, blank=True, null=True)
    total_depenses_usd = models.DecimalField(max_digits=15, decimal_places=2, default=0, blank=True, null=True)

    def __str__(self):
        return self.nom_annee

    

# 💱 Taux de change
class Taux(models.Model):
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    valeur = models.DecimalField(max_digits=10, decimal_places=2, help_text="Taux de conversion USD → CDF")
    date_taux = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.annee_scolaire.nom_annee} → 1 USD = {self.valeur} CDF"

# 🏫 Classe
class Classes(models.Model):
    nom_classe = models.CharField(max_length=100)
    montant = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # CDF
    montant_usd = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)  # USD
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nom_classe

# 🧾 Autres frais (inscription, etc.)
class AutreFrais(models.Model):
    description = models.CharField(max_length=255)
    montant_cdf = models.DecimalField(max_digits=10, decimal_places=2)
    montant_usd = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.description

# 👦 Élève
class student(models.Model):
    nom = models.CharField(max_length=100)
    post_nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    classe = models.ForeignKey(Classes, on_delete=models.CASCADE)
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    date_naissance = models.DateField()
    sexe = models.CharField(max_length=10, choices=[('M', 'Masculin'), ('F', 'Féminin')])
    nom_pere = models.CharField(max_length=100)
    nom_mere = models.CharField(max_length=100)
    telephone = models.CharField(max_length=15)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'student'
        verbose_name_plural = 'students'

    def __str__(self):
        return f'{self.nom} {self.post_nom} {self.prenom}'

from decimal import Decimal
from django.db.models import Sum
from django.db import models

class Paiement(models.Model):
    TYPE_PAIEMENT_CHOICES = [
        ('minerval', 'Minerval'),
        ('autre_frais', 'Autre Frais'),
    ]

    DEVISE_CHOICES = [
        ('cdf', 'Franc Congolais'),
        ('usd', 'Dollar'),
        ('mixte', 'Mixte'),
    ]

    taux = models.ForeignKey('Taux', on_delete=models.SET_NULL, null=True, blank=True)
    eleve = models.ForeignKey('student', on_delete=models.CASCADE)
    classe = models.ForeignKey('Classes', on_delete=models.CASCADE)
    annee_scolaire = models.ForeignKey('AnneeScolaire', on_delete=models.CASCADE)
    created_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True)

    mois = models.CharField(
        max_length=20,
        choices=[(m.lower(), m.title()) for m in [
            'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
            'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'
        ]]
    )

    montant = models.DecimalField(max_digits=10, decimal_places=2)
    montant_usd_brut = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    montant_cdf_brut = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    object_paiement = models.CharField(max_length=50)
    date_paiement = models.DateField(auto_now_add=True)
    recu = models.BooleanField(default=False)
    type_paiement = models.CharField(max_length=20, choices=TYPE_PAIEMENT_CHOICES, default='autre_frais')
    devise = models.CharField(max_length=10, choices=DEVISE_CHOICES, default='cdf')
    avance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    solde = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.eleve.nom} {self.eleve.post_nom} {self.eleve.prenom}'
    
# 📉 Dépenses
class DescriptionDepense(models.Model):
    description = models.CharField(max_length=255)
    ecole = models.ForeignKey(Ecole, on_delete=models.CASCADE, null=True, blank=True)
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    user_cible = models.ForeignKey(User, on_delete=models.CASCADE, related_name='descriptions_utilisables')

    class Meta:
        unique_together = ('description', 'ecole', 'annee_scolaire', 'user_cible')

    def __str__(self):
        return self.description
    
class Depense(models.Model):
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    description = models.ForeignKey(DescriptionDepense, on_delete=models.SET_NULL, null=True, blank=True)
    montant = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    montant_usd = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    date_depense = models.DateField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.description} - CDF:{self.montant} | USD:{self.montant_usd}"
