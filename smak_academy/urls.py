
from django.contrib import admin
from django.urls import path
from academy import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Connexion/Création compte
    #path('register/', views.register, name='register'),
    path('', views.login_view, name='login'),
    
    # Se déconnecter
    path('logout/', views.logout_view, name='logout'),
    
    # Autres vues
    path('index/', views.index, name='index'),
    path('inscription/', views.inscription, name='inscription'),
    path('details_classe/', views.details_classe, name='details_classe'),
    path('paiements/', views.paiements, name='paiements'),
    path('details_paiements/', views.details_paiements, name='details_paiements'),
    path('add_class/', views.add_class, name='add_class'),
    path('add_year/', views.add_year, name='add_year'),
    path('changer_annee/', views.changer_annee, name='changer_annee'),
    path('api/eleves/<int:classe_id>/', views.get_eleves_by_classe, name='get_eleves_by_classe'),
    path('get-classes/<int:annee_id>/', views.get_classes_by_annee, name='get_classes_by_annee'),
    path('insolvables/', views.eleves_non_payeurs, name='insolvables'),

    # Exportation en Excel
    path('export_paiements_excel/', views.export_paiements_excel, name='export_paiements_excel'),
    path('export_insolvable_excel/', views.export_insolvable_excel, name='export_insolvable_excel'),
    path('export-eleves-excel/', views.export_eleves_excel, name='export_eleves_excel'),

    # Étudiants
    path('student/<int:id>/', views.Details_Student, name='Details_Student'),
    path('student/update/<int:id>/', views.UpdateStudent, name='UpdateStudent'),
    path('student/delete/<int:id>/', views.DeleteStudent, name='DeleteStudent'),

    # Années
    path('year/update/<int:id>/', views.UpdateYear, name='UpdateYear'),
    path('year/delete/<int:id>/', views.DeleteYear, name='DeleteYear'),

    # Classes
    path('classe/update/<int:id>/', views.UpdateClasse, name='UpdateClasse'),
    path('classe/delete/<int:id>/', views.DeleteClasse, name='DeleteClasse'),

    # AJAX
    path('ajax/load-eleves/', views.load_eleves, name='load_eleves'),
    path('search_students/', views.search_students, name='search_students'),
    path('get_montant_minerval/<int:classe_id>/', views.get_montant_minerval, name='get_montant_minerval'),
    path('get-eleves/<int:classe_id>/', views.get_eleves, name='get_eleves'),

    # Reçu
    path('receipt/<int:paiement_id>/', views.receipt_view, name='receipt_view'),

    # Rapports
    path('rapport-paiements-jour/', views.rapport_paiements_jour, name='rapport_paiements_jour'),
    path('rapport-mensuel/', views.rapport_mensuel, name='rapport_mensuel'),
    path('rapport_annuel/', views.rapport_annuel, name='rapport_annuel'),

    # Exportation rapports
    path('export-rapport-journalier/', views.export_rapport_journalier_excel, name='export_rapport_journalier_excel'),
    path('export-rapport-mensuel/', views.export_rapport_mensuel_excel, name='export_rapport_mensuel_excel'),
    path('export-rapport-annuel/', views.export_rapport_annuel_excel, name='export_rapport_annuel_excel'),

    # Dépenses
    path('ajouter-depense/', views.ajouter_depense, name='ajouter_depense'),
    path('rapport-financier/', views.rapport_financier, name='rapport_financier'),
    path('rapport-financier/export-excel/', views.export_rapport_excel, name='export_rapport_excel'),
    path('rapport-financier/export-pdf/', views.export_rapport_pdf, name='export_rapport_pdf'),
    path('toutes-les-depenses/', views.voir_toutes_les_depenses, name='voir_toutes_les_depenses'),
    path('dettes-details/', views.dettes_details, name='dettes_details'),
    path('eleve-dette/<int:eleve_id>/', views.details_eleve_dette, name='details_eleve_dette'),
    path('eleves-en-retard/', views.eleves_en_retard, name='eleves_en_retard'),

    # Autres frais
    path('ajouter-autre-frais/', views.ajouter_autre_frais, name='ajouter_autre_frais'),
    path('modifier-autre-frais/<int:id>/', views.UpdateAutreFrais, name='UpdateAutreFrais'),
    path('supprimer-autre-frais/<int:id>/', views.DeleteAutreFrais, name='DeleteAutreFrais'),

    # API pour charger les autres frais
    path('get-autre-frais/', views.get_autre_frais_options, name='get_autre_frais_options'),

    # Taux
    path('ajout-taux/', views.enregistrer_taux, name='ajout_taux'),
    path('modifier-taux/<int:taux_id>/', views.modifier_taux, name='modifier_taux'),
    path('supprimer-taux/<int:taux_id>/', views.supprimer_taux, name='supprimer_taux'),

    # AJAX Inscription
    path('get-inscription-fee/', views.get_inscription_fee, name='get_inscription_fee'),
    path('depenses/export/', views.exporter_depenses_pdf, name='exporter_depenses_pdf'),
    
    # Promo
    path('promo/index_promo', views.index_promo, name='index_promo'),

    path('promo/dashboard/', views.dashboard_promo, name='dashboard_promo'),
    path('promo/comptables/', views.liste_comptables, name='liste_comptables'),
    path('promo/comptables/ajouter/', views.register, name='register'),
    path('promo/comptables/<int:id>/', views.details_comptable, name='details_comptable'),
    
     path('user-autocomplete/', views.UserAutocomplete.as_view(), name='user-autocomplete'),
    path('annee-autocomplete/', views.AnneeAutocomplete.as_view(), name='annee-autocomplete'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT)

