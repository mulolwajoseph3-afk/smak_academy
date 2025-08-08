from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User, Ecole, Paiement, Classes, AnneeScolaire, Depense, AutreFrais, student, Taux

from django.contrib.auth.forms import AuthenticationForm
from decimal import Decimal
from django import forms
from django.contrib.auth.forms import AuthenticationForm

class UserLoginForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
        self.fields['username'].widget = forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Nom d'utilisateur"
        })
        self.fields['password'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': "Mot de passe"
        })
        
from django import forms
from academy.models import User

class RegisterForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Nom d\'utilisateur',
        'class': 'form-control'
    }), required=True)

    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'Email (optionnel)',
        'class': 'form-control'
    }), required=False)  # ✅ Très important

    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Mot de passe',
        'class': 'form-control'
    }), required=True)

    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirmer le mot de passe',
        'class': 'form-control'
    }), required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        email = cleaned_data.get('email')

        if password != password_confirm:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")

        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("Un utilisateur avec cet email existe déjà.")

        return cleaned_data

from django import forms
from academy.models import User

class UserCreationForm(forms.ModelForm):
    raw_password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput,
        required=True
    )
    raw_password_confirm = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput,
        required=True
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'nom_complet', 'role', 'ecole', 'is_active']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("raw_password")
        confirm = cleaned_data.get("raw_password_confirm")

        if password and confirm and password != confirm:
            self.add_error('raw_password_confirm', "Les mots de passe ne correspondent pas.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('raw_password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user
    
class StudentRegistration(forms.ModelForm):
    montant_inscription = forms.DecimalField(
        label="Frais d'inscription",
        required=False,
        min_value=0,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
            'placeholder': 'Montant auto chargé'
        })
    )

    devise_inscription = forms.ChoiceField(
        label="Devise utilisée",
        choices=[('cdf', 'Franc congolais'), ('usd', 'Dollar')],
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        self.annee_scolaire_id = kwargs.pop('annee_scolaire_id', None)
        self.created_by = kwargs.pop('created_by', None)
        super().__init__(*args, **kwargs)

        # 🎯 Filtrer les classes créées par ce comptable
        if self.annee_scolaire_id and self.created_by:
            self.fields['classe'].queryset = Classes.objects.filter(
                annee_scolaire_id=self.annee_scolaire_id,
                created_by=self.created_by
            )
        else:
            self.fields['classe'].queryset = Classes.objects.none()

        # 💰 Charger automatiquement le montant selon la devise
        frais = AutreFrais.objects.filter(
            description='inscription',
            annee_scolaire_id=self.annee_scolaire_id
        ).first()

        devise = self.data.get('devise_inscription')
        if frais:
            if devise == 'cdf':
                self.fields['montant_inscription'].initial = frais.montant_cdf
            elif devise == 'usd':
                self.fields['montant_inscription'].initial = frais.montant_usd

        # 📅 Pré-remplir la date de naissance si existante
        if self.instance and self.instance.date_naissance:
            self.fields['date_naissance'].initial = self.instance.date_naissance.strftime('%Y-%m-%d')

    def save(self, commit=True):
        instance = super().save(commit=False)

        if self.annee_scolaire_id:
            instance.annee_scolaire_id = self.annee_scolaire_id
        if self.created_by:
            instance.created_by = self.created_by

        if commit:
            instance.save()

            montant = self.cleaned_data.get('montant_inscription')
            devise = self.cleaned_data.get('devise_inscription')

            if montant and devise:
                paiement_data = {
                    'eleve': instance,
                    'classe': instance.classe,
                    'annee_scolaire': instance.annee_scolaire,
                    'type_paiement': 'autre_frais',
                    'object_paiement': 'frais_inscription',
                    'mois': 'septembre',
                    'recu': True,
                    'devise': devise,
                    'montant': Decimal('0.00'),
                    'created_by': self.created_by
                }

                if devise == 'cdf':
                    paiement_data['montant_cdf_brut'] = montant
                elif devise == 'usd':
                    paiement_data['montant_usd_brut'] = montant

                self.paiement_created = Paiement.objects.create(**paiement_data)

        return instance

    class Meta:
        model = student
        fields = [
            'nom', 'post_nom', 'prenom', 'classe', 'date_naissance',
            'sexe', 'nom_pere', 'nom_mere', 'telephone'
        ]
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'post_nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Post Nom'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'classe': forms.Select(attrs={'class': 'form-select'}),
            'date_naissance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'sexe': forms.Select(attrs={'class': 'form-select'}),
            'nom_pere': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du père'}),
            'nom_mere': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de la mère'}),
            'telephone': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'tel',
                'placeholder': '+243 999 999 999'
            }),
        }

class ClassesRegistratation(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.created_by = kwargs.pop('created_by', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.created_by:
            instance.created_by = self.created_by
        if commit:
            instance.save()
        return instance

    class Meta:
        model = Classes
        exclude = ['annee_scolaire']
        widgets = {
            'nom_classe': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de la classe'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Minerval (CDF)'}),
            'montant_usd': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Minerval (USD)'})
        }

    def clean(self):
        data = super().clean()
        if not data.get("montant") and not data.get("montant_usd"):
            raise ValidationError("Veuillez indiquer au moins un montant.")
        return data


class AnneeScolaireRegistration(forms.ModelForm):
    class Meta:
        model = AnneeScolaire
        fields = ['nom_annee']
        widgets = {
            'nom_annee': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Entrez l'année scolaire : 2025-2026"
            })
        }
        
        
from django import forms
from decimal import Decimal
from academy.models import Paiement, student, Taux



class PaiementRegistration(forms.ModelForm):
    eleve = forms.ModelChoiceField(
        queryset=student.objects.none(),
        empty_label="Sélectionnez un élève",
        required=True
    )

    devise = forms.ChoiceField(
        choices=[('cdf', 'Franc Congolais'), ('usd', 'Dollar'), ('mixte', 'Mixte')],
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': 'required',
            'id': 'id_devise'
        }),
        required=True
    )

    montant_cdf = forms.DecimalField(
        max_digits=10, decimal_places=2, required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Montant payé en Francs (CDF)',
            'id': 'id_montant_cdf'
        })
    )

    montant_usd = forms.DecimalField(
        max_digits=10, decimal_places=2, required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Montant payé en Dollars (USD)',
            'id': 'id_montant_usd'
        })
    )

    def __init__(self, *args, **kwargs):
        self.annee_scolaire_id = kwargs.pop('annee_scolaire_id', None)
        self.created_by = kwargs.pop('created_by', None)
        super().__init__(*args, **kwargs)

        # 🎯 Élève filtré par classe
        classe_id = self.data.get('classe') or (self.instance.classe.id if self.instance.pk else None)
        if classe_id:
            try:
                self.fields['eleve'].queryset = student.objects.filter(classe_id=int(classe_id))
            except (ValueError, TypeError):
                self.fields['eleve'].queryset = student.objects.none()
        else:
            self.fields['eleve'].queryset = student.objects.none()

        # ✅ Objet paiement : tous les objets enregistrés
        objets = Paiement.objects.filter(
            annee_scolaire_id=self.annee_scolaire_id,
            created_by=self.created_by
        ).values_list('object_paiement', flat=True).distinct()

        self.fields['object_paiement'] = forms.ChoiceField(
            choices=[('', '--- Sélectionner ---')] + [(obj, obj) for obj in objets if obj],
            required=False,
            widget=forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_object_paiement'
            })
        )

    def clean_eleve(self):
        eleve = self.cleaned_data.get('eleve')
        if not eleve:
            raise ValidationError("Veuillez sélectionner un élève valide.")
        if self.annee_scolaire_id and eleve.classe.annee_scolaire_id != self.annee_scolaire_id:
            raise ValidationError("L'élève ne correspond pas à l'année scolaire sélectionnée.")
        return eleve

    def save(self, commit=True):
        paiement = super().save(commit=False)
        if self.annee_scolaire_id:
            paiement.annee_scolaire_id = self.annee_scolaire_id
        if self.created_by:
            paiement.created_by = self.created_by
        paiement.devise = self.cleaned_data.get('devise')
        if commit:
            paiement.save()
        return paiement

    class Meta:
        model = Paiement
        fields = [
            'classe', 'eleve', 'mois', 'montant', 'object_paiement',
            'recu', 'type_paiement', 'avance', 'devise'
        ]
        widgets = {
            'classe': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required',
                'id': 'classe-select'
            }),
            'mois': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required',
                'id': 'id_mois'
            }),
            'montant': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Montant à payer',
                'required': 'required',
                'readonly': 'readonly',
                'id': 'id_montant'
            }),
            'recu': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'type_paiement': forms.Select(attrs={'class': 'form-select'}),
            'avance': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Avance'
            }),
        }

        

from django import forms
from .models import Classes

class MoisClasseFilterForm(forms.Form):
    MOIS_CHOICES = [
        ('01', 'Janvier'),
        ('02', 'Février'),
        ('03', 'Mars'),
        ('04', 'Avril'),
        ('05', 'Mai'),
        ('06', 'Juin'),
        ('07', 'Juillet'),
        ('08', 'Août'),
        ('09', 'Septembre'),
        ('10', 'Octobre'),
        ('11', 'Novembre'),
        ('12', 'Décembre'),
    ]

    mois = forms.ChoiceField(
        choices=MOIS_CHOICES,
        label="Choisissez un mois",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    classe = forms.ChoiceField(
        label="Choisissez une classe",
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False
    )

    def __init__(self, *args, annee=None, promo=None, **kwargs):
        super().__init__(*args, **kwargs)

        # 📦 Classes créées par des comptables de l’école du promo
        if annee and promo and promo.role == 'promo':
            classes_filtrees = Classes.objects.filter(
                annee_scolaire=annee,
                annee_scolaire__ecole=promo.ecole,
                created_by__role='comptable'
            )

            self.fields['classe'].choices = [
                ('', 'Toutes les classes')
            ] + [(c.id, c.nom_classe) for c in classes_filtrees]
        else:
            self.fields['classe'].choices = [('', 'Aucune classe trouvée')]

from django import forms
from .models import Classes

class ClasseFilterForm(forms.Form):
    classe = forms.ModelChoiceField(
        queryset=Classes.objects.none(),
        required=False,
        label="Classe",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, annee=None, promo=None, **kwargs):
        super().__init__(*args, **kwargs)
        if annee and promo and promo.role == 'promo':
            classes_filtrees = Classes.objects.filter(
                annee_scolaire=annee,
                annee_scolaire__ecole=promo.ecole,
                created_by__role='comptable'
            )
            self.fields['classe'].queryset = classes_filtrees

from django.core.exceptions import ValidationError
from django import forms
from .models import Depense

from django import forms
from django.core.exceptions import ValidationError
from .models import Depense, DescriptionDepense
from django import forms
from django.core.exceptions import ValidationError
from .models import Depense, DescriptionDepense

from django import forms
from dal import autocomplete
from .models import DescriptionDepense

class DescriptionDepenseForm(forms.ModelForm):
    class Meta:
        model = DescriptionDepense
        fields = '__all__'
        widgets = {
            'user_cible': autocomplete.ModelSelect2(url='user-autocomplete', forward=['ecole']),
            'annee_scolaire': autocomplete.ModelSelect2(url='annee-autocomplete', forward=['ecole']),
        }

from .models import DescriptionDepense

class DepenseForm(forms.ModelForm):
    description = forms.ModelChoiceField(
        queryset=DescriptionDepense.objects.none(),
        required=False,
        label="Description",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_description'})
    )

    class Meta:
        model = Depense
        fields = ['description', 'montant', 'montant_usd']
        widgets = {
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Montant en CDF'}),
            'montant_usd': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Montant en USD'}),
        }

    def __init__(self, *args, **kwargs):
        self.created_by = kwargs.pop('created_by', None)
        self.annee_scolaire = kwargs.pop('annee_scolaire', None)
        super().__init__(*args, **kwargs)

        if self.created_by and self.annee_scolaire:
            self.fields['description'].queryset = DescriptionDepense.objects.filter(
                annee_scolaire=self.annee_scolaire,
                user_cible=self.created_by
            )

            # Ajoute une option "Autre" manuellement
            self.fields['description'].choices = list(self.fields['description'].choices) + [('', '---------'), ('autre', 'Autre')]

    def save(self, commit=True):
        instance = super().save(commit=False)

        desc = self.cleaned_data.get("description")
        if desc == "autre" or desc is None:
            desc_text = self.data.get("description_autre")
            if desc_text:
                obj, _ = DescriptionDepense.objects.get_or_create(
                    description=desc_text,
                    annee_scolaire=self.annee_scolaire,
                    user_cible=self.created_by,
                    defaults={'ecole': self.created_by.ecole}
                )
                instance.description = obj
        else:
            instance.description = desc  # ✅ C'est déjà une instance

        if self.created_by:
            instance.created_by = self.created_by
        if commit:
            instance.save()
        return instance


from .models import AutreFrais

class AutreFraisForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.created_by = kwargs.pop('created_by', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.created_by:
            instance.created_by = self.created_by
        if commit:
            instance.save()
        return instance

    class Meta:
        model = AutreFrais
        fields = ['description', 'montant_cdf', 'montant_usd']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description du frais'}),
            'montant_cdf': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Montant en Franc Congolais'}),
            'montant_usd': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Montant en Dollar'}),
        }

from .models import Taux

from django.core.exceptions import ValidationError

class TauxRegistration(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.created_by = kwargs.pop('created_by', None)
        super().__init__(*args, **kwargs)

    def clean_valeur(self):
        valeur = self.cleaned_data.get('valeur')

        # 💡 Vérification manuelle (même si NumberInput est utilisé)
        if valeur is None:
            raise ValidationError("Veuillez entrer une valeur numérique.")

        return valeur

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.created_by:
            instance.created_by = self.created_by
        if commit:
            instance.save()
        return instance

    class Meta:
        model = Taux
        fields = ['valeur']
        widgets = {
            'valeur': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Taux actuel (ex: 2500)',
                'required': 'required'
            })
        }
        
#details depense mois 

from django import forms
from .models import DescriptionDepense

MOIS_CHOICES = [
    ('', '--- Tous les mois ---'),
    ('1', 'Janvier'), ('2', 'Février'), ('3', 'Mars'), ('4', 'Avril'),
    ('5', 'Mai'), ('6', 'Juin'), ('7', 'Juillet'), ('8', 'Août'),
    ('9', 'Septembre'), ('10', 'Octobre'), ('11', 'Novembre'), ('12', 'Décembre'),
]

class FiltreDepenseForm(forms.Form):
    mois = forms.ChoiceField(
        choices=MOIS_CHOICES,
        required=False,
        label="Mois",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    description = forms.ModelChoiceField(
        queryset=DescriptionDepense.objects.all(),
        required=False,
        label="Description",
        empty_label="--- Toutes les descriptions ---",
        widget=forms.Select(attrs={'class': 'form-control'})
    )