# Résolution de problèmes - Générateur automatique d'emploi du temps

## Problème : `generate_schedule() got an unexpected keyword argument 'start_date'`

### Cause

Ce problème se produit lorsque Streamlit utilise une version en cache de l'ancien module `scheduler.py` qui n'avait pas les nouveaux paramètres.

### Solution

**Redémarrer Streamlit** pour forcer le rechargement des modules :

1. **Arrêtez Streamlit** :
   - Appuyez sur `Ctrl+C` dans le terminal où Streamlit tourne
   - Ou fermez la fenêtre du terminal

2. **Redémarrez Streamlit** :
   ```bash
   streamlit run frontend/app.py
   ```

3. **Rafraîchissez votre navigateur** :
   - Appuyez sur `F5` ou `Ctrl+R` pour recharger la page

### Vérification

Pour vérifier que la fonction est correctement chargée :

1. Ouvrez la console Python dans Streamlit (si disponible)
2. Ou vérifiez que les paramètres apparaissent dans l'interface :
   - Date de début
   - Heure de début
   - Durée
   - Maximum par jour

Si ces paramètres apparaissent, la nouvelle version est chargée.

### Alternative : Vider le cache de Streamlit

Si le redémarrage ne fonctionne pas :

1. **Supprimez le cache de Streamlit** :
   ```bash
   # Sur Windows
   rmdir /s "%USERPROFILE%\.streamlit\cache"
   
   # Sur Linux/Mac
   rm -rf ~/.streamlit/cache
   ```

2. **Redémarrez Streamlit**

### Vérification de la signature de la fonction

Pour vérifier que la fonction a la bonne signature :

```python
from backend.optimization.scheduler import generate_schedule
import inspect

sig = inspect.signature(generate_schedule)
print(sig)
# Devrait afficher :
# (start_date=None, start_time=datetime.time(9, 0), duration_minutes=120, time_slots_per_day=4)
```

### Test de la fonction

Vous pouvez tester la fonction directement :

```python
from backend.optimization.scheduler import generate_schedule
from datetime import date, time

result = generate_schedule(
    start_date=date.today(),
    start_time=time(9, 0),
    duration_minutes=120,
    time_slots_per_day=4
)

print(result)
```

Si cela fonctionne, le problème vient du cache de Streamlit.

## Autres problèmes possibles

### Problème : Aucun examen n'est programmé

**Solutions** :
1. Vérifiez qu'il y a des modules sans examen
2. Vérifiez qu'il y a des professeurs disponibles
3. Vérifiez qu'il y a des salles avec capacité suffisante
4. Essayez avec une date plus éloignée

### Problème : Erreur de contrainte

Si vous obtenez une erreur de contrainte (ex: "Un étudiant ne peut pas avoir deux examens en même temps") :

1. C'est normal - le système respecte les contraintes
2. Le module sera marqué comme "échoué" dans les résultats
3. Vous pouvez le programmer manuellement plus tard

## Conclusion

Le problème le plus courant est le **cache de Streamlit**. La solution la plus simple est de **redémarrer Streamlit**.
