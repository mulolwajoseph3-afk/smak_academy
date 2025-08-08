from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from academy.models import User, Ecole, AnneeScolaire

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserCreationForm
from academy.models import User, Ecole, AnneeScolaire

# 💼 Formulaire personnalisé pour inclure raw_password
class UserAdminForm(forms.ModelForm):
    raw_password = forms.CharField(required=False, label="Mot de passe (non chiffré)", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = '__all__'
        
        
# 👤 Admin utilisateur avec raw_password visible
@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    form = UserAdminForm           # ← utilisé pour édition
    add_form = UserCreationForm    # ← utilisé à la création

    list_display = ['username', 'nom_complet', 'email', 'role', 'ecole', 'is_active']
    list_filter = ['role', 'ecole']
    search_fields = ['username', 'email', 'nom_complet']

    fieldsets = (
        (None, {
            'fields': ('username', 'email', 'nom_complet', 'role', 'ecole', 'is_active')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'nom_complet', 'role', 'ecole', 'is_active', 'raw_password', 'raw_password_confirm'),
        }),
    )

# 🏫 École
@admin.register(Ecole)
class EcoleAdmin(admin.ModelAdmin):
    list_display = ['nom', 'logo']
    search_fields = ['nom']

# 📅 Année scolaire
@admin.register(AnneeScolaire)
class AnneeScolaireAdmin(admin.ModelAdmin):
    list_display = ['nom_annee', 'ecole', 'active']
    list_filter = ['ecole', 'active']
    search_fields = ['nom_annee']

from django.contrib import admin
from .models import DescriptionDepense, User
from django.contrib import admin
from django import forms
from .models import DescriptionDepense, User, AnneeScolaire, Ecole

from django import forms
from .models import DescriptionDepense, User, AnneeScolaire

from django.contrib import admin
from .models import DescriptionDepense
from .forms import DescriptionDepenseForm

class DescriptionDepenseAdmin(admin.ModelAdmin):
    form = DescriptionDepenseForm
    list_display = ['description', 'ecole', 'annee_scolaire', 'user_cible']
    list_filter = ['ecole', 'annee_scolaire']
    search_fields = ['description']

admin.site.register(DescriptionDepense, DescriptionDepenseAdmin)
