from .models import AnneeScolaire

def annee_scolaire_context(request):
    annee_scolaire_id = request.session.get('annee_scolaire')
    annee_scolaire = None

    if request.user.is_authenticated:
        try:
            if annee_scolaire_id:
                # 🔍 Chargement contrôlé : seulement si l'année scolaire appartient à l'école du user
                annee = AnneeScolaire.objects.get(id=annee_scolaire_id, ecole=request.user.ecole)
                annee_scolaire = annee
            else:
                # 🔁 Optionnel : charger la première année active si aucune sélection
                annee_scolaire = AnneeScolaire.objects.filter(ecole=request.user.ecole, active=True).first()
        except AnneeScolaire.DoesNotExist:
            annee_scolaire = None

    return {
        'annee_scolaire_active': annee_scolaire
    }