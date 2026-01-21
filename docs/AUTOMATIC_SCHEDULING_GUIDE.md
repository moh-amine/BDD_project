# Guide d'utilisation - Génération automatique d'emploi du temps

## Vue d'ensemble

La fonctionnalité de **génération automatique d'emploi du temps** permet de programmer automatiquement des examens pour tous les modules qui n'ont pas encore d'examen programmé.

## Comment ça fonctionne

### Algorithme intelligent

Le système utilise un algorithme qui :

1. **Trouve les modules sans examen** : Identifie tous les modules qui n'ont pas encore d'examen programmé
2. **Sélectionne intelligemment** :
   - **Professeur** : Préfère un professeur du même département que le module
   - **Salle** : Choisit une salle avec une capacité suffisante pour tous les étudiants de la formation
   - **Créneau horaire** : Trouve un créneau disponible sans conflit
3. **Respecte toutes les contraintes** :
   - ✅ Pas de chevauchement pour les étudiants (même formation)
   - ✅ Pas de chevauchement pour les professeurs
   - ✅ Capacité de salle suffisante
   - ✅ Pas de conflit de salle
4. **Distribue sur plusieurs jours** : Si nécessaire, répartit les examens sur plusieurs jours

## Comment utiliser

### Étape 1 : Accéder à la fonctionnalité

1. Connectez-vous en tant qu'**ADMIN**
2. Allez dans le menu **"⚙️ Planification automatique"**

### Étape 2 : Configurer les paramètres

Vous pouvez personnaliser :

- **Date de début** : Date à partir de laquelle commencer la planification
- **Heure de début** : Heure du premier examen (par défaut: 09:00)
- **Durée** : Durée de chaque examen en minutes (par défaut: 120 minutes)
- **Maximum par jour** : Nombre maximum d'examens par jour (par défaut: 4)

### Étape 3 : Générer l'emploi du temps

1. Cliquez sur le bouton **"🚀 Générer emploi du temps automatiquement"**
2. Attendez que le système traite tous les modules
3. Consultez les résultats détaillés

### Étape 4 : Consulter les résultats

Le système affiche :

- **✅ Réussis** : Nombre d'examens programmés avec succès
- **❌ Échoués** : Nombre de modules qui n'ont pas pu être programmés
- **📋 Total** : Nombre total de modules sans examen

**Détails** :
- Liste des examens programmés avec leurs informations (date, heure, professeur, salle)
- Liste des modules non programmés avec la raison

## Exemple d'utilisation

### Scénario 1 : Planification simple

1. **Configuration** :
   - Date de début : Demain
   - Heure de début : 09:00
   - Durée : 120 minutes
   - Maximum par jour : 4

2. **Résultat attendu** :
   - Les examens sont programmés à 09:00, 11:00, 14:00, 16:00
   - Si plus de 4 modules, les suivants sont programmés le jour suivant

### Scénario 2 : Planification avec contraintes

Si un module ne peut pas être programmé, le système :
1. Essaie différents créneaux horaires
2. Essaie différents jours (jusqu'à 10 jours)
3. Si toujours impossible, marque le module comme "échoué" avec la raison

## Contraintes respectées automatiquement

Le système respecte **toutes** les contraintes de la base de données :

1. ✅ **Un examen par module** : Chaque module ne peut avoir qu'un seul examen
2. ✅ **Pas de chevauchement étudiant** : Les étudiants d'une même formation ne peuvent pas avoir deux examens en même temps
3. ✅ **Pas de chevauchement professeur** : Un professeur ne peut pas surveiller deux examens simultanément
4. ✅ **Capacité de salle** : La salle doit avoir une capacité suffisante pour tous les étudiants
5. ✅ **Pas de conflit de salle** : Une salle ne peut pas accueillir deux examens en même temps

## Cas d'échec possibles

Un module peut ne pas être programmé si :

- ❌ **Aucun professeur disponible** : Tous les professeurs ont déjà des examens aux créneaux disponibles
- ❌ **Aucune salle disponible** : Toutes les salles sont occupées ou n'ont pas la capacité suffisante
- ❌ **Contraintes trop strictes** : Les contraintes (étudiants, professeurs) empêchent toute programmation

## Conseils d'utilisation

### Pour de meilleurs résultats :

1. **Vérifiez les ressources** :
   - Assurez-vous d'avoir suffisamment de professeurs
   - Vérifiez que les salles ont des capacités suffisantes

2. **Planifiez à l'avance** :
   - Utilisez une date de début suffisamment éloignée
   - Cela donne plus de flexibilité au système

3. **Ajustez les paramètres** :
   - Augmentez le "maximum par jour" si vous avez beaucoup de modules
   - Réduisez la durée si nécessaire

4. **Vérifiez les résultats** :
   - Consultez toujours les détails pour comprendre les échecs
   - Vous pouvez ensuite programmer manuellement les modules échoués

## Fonction technique

### Code backend

La fonction `generate_schedule()` dans `backend/optimization/scheduler.py` :

```python
def generate_schedule(
    start_date=None,        # Date de début (défaut: demain)
    start_time=time(9, 0),  # Heure de début (défaut: 09:00)
    duration_minutes=120,   # Durée en minutes (défaut: 120)
    time_slots_per_day=4   # Maximum par jour (défaut: 4)
)
```

### Retour de la fonction

```python
{
    'success': int,      # Nombre d'examens programmés
    'failed': int,        # Nombre de modules non programmés
    'total': int,         # Total de modules sans examen
    'details': list       # Détails de chaque module
}
```

## Résolution de problèmes

### Problème : Aucun examen n'est programmé

**Solutions** :
1. Vérifiez qu'il y a des modules sans examen
2. Vérifiez qu'il y a des professeurs disponibles
3. Vérifiez qu'il y a des salles avec capacité suffisante
4. Essayez avec une date plus éloignée

### Problème : Certains modules échouent

**Solutions** :
1. Consultez les détails pour voir la raison
2. Programmez manuellement ces modules
3. Ajoutez plus de professeurs ou de salles si nécessaire

## Conclusion

La génération automatique d'emploi du temps est un outil puissant qui :
- ✅ Économise du temps
- ✅ Respecte toutes les contraintes
- ✅ Optimise l'utilisation des ressources
- ✅ Fournit des résultats détaillés

Utilisez cette fonctionnalité pour planifier rapidement tous vos examens !
