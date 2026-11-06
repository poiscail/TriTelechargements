# TriTelechargements

Surveille le dossier Téléchargements et range chaque **nouveau** fichier dans un sous-dossier selon son extension (Images, Documents, Vidéos, Musique, Archives, Installateurs).

## Utilisation

1. Dossier surveillé : `regles.json` → `"dossier"` (par défaut `"%USERPROFILE%/Downloads"`).
2. Double-cliquer sur `Lancer.bat`. Fermer la fenêtre (ou Ctrl+C) pour arrêter.

Nécessite Python 3.

## Règles (`regles.json`)

- `categories` : nom du sous-dossier → liste d'extensions.
- `ignorer` : noms jamais touchés (par défaut `Outils`).
- `en_cours` : extensions des téléchargements en cours, ignorées.

## Sécurité

- Déplace seulement : rien n'est supprimé ni écrasé (doublon → `nom (1).ext`).
- Les fichiers présents au lancement, les dossiers et les extensions inconnues ne sont pas touchés.

## Test

```
python test_tri.py
```
