# TriTelechargements

Surveille le dossier Téléchargements et range chaque **nouveau** fichier dans un sous-dossier selon son extension (Images, Documents, Vidéos, Musique, Archives, Installateurs).

## Utilisation

1. Dossier surveillé : `regles.json` → `"dossier"` (par défaut `"%USERPROFILE%/Downloads"`).
2. Double-cliquer sur `TriTelechargements.exe` (rien à installer ; [téléchargement](https://github.com/poiscail/TriTelechargements/releases/latest)). Une fenêtre sombre s'ouvre : bouton Démarrer/Arrêter, liste des derniers fichiers rangés (double-clic pour le montrer dans l'Explorateur), bouton pour ouvrir le dossier, et « Ranger l'existant… » qui montre d'abord ce qui sera déplacé puis demande confirmation. Fermer la fenêtre pour quitter.

Sans .exe : `Lancer.bat` (nécessite Python 3). Pour refaire l'exe :

```
pip install pyinstaller
pyinstaller --onefile --noconsole --name TriTelechargements --add-data "regles.json;." --distpath . tri.py
```

## Règles (`regles.json`)

L'exe utilise le `regles.json` placé à côté de lui, sinon les règles par défaut.


- `categories` : nom du sous-dossier → liste d'extensions.
- `ignorer` : noms jamais touchés (par défaut `Outils`).
- `en_cours` : extensions des téléchargements en cours, ignorées (un fichier qui a encore son `.part`/`.crdownload` à côté attend aussi).

## Sécurité

- Déplace seulement : rien n'est supprimé ni écrasé (doublon → `nom (1).ext`).
- Les fichiers présents au lancement ne sont touchés que via « Ranger l'existant… », après confirmation. Les dossiers et les extensions inconnues ne sont jamais touchés.

## Test

```
python test_tri.py
```
