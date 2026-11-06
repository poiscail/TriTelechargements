# TriTelechargements

Surveille le dossier Téléchargements et range chaque **nouveau** fichier dans un sous-dossier selon son extension (Images, Documents, Vidéos, Musique, Archives, Installateurs).

## Utilisation

1. Dossier surveillé : `regles.json` → `"dossier"` (par défaut `"%USERPROFILE%/Downloads"`).
2. Double-cliquer sur `TriTelechargements.exe` (rien à installer ; [téléchargement](https://github.com/poiscail/TriTelechargements/releases/latest)). Fermer la fenêtre pour arrêter.

Sans .exe : `Lancer.bat` (nécessite Python 3). Pour refaire l'exe :

```
pip install pyinstaller
pyinstaller --onefile --name TriTelechargements --add-data "regles.json;." --distpath . tri.py
```

## Règles (`regles.json`)

L'exe utilise le `regles.json` placé à côté de lui, sinon les règles par défaut.


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
