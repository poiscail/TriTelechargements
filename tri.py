"""Surveille un dossier et range chaque nouveau fichier selon son extension."""
import json, os, sys, time
from pathlib import Path

CONFIG = Path(__file__).with_name("regles.json")


def charger():
    regles = json.loads(CONFIG.read_text(encoding="utf-8"))
    ext_vers_dossier = {e.lower(): nom for nom, exts in regles["categories"].items() for e in exts}
    return regles, ext_vers_dossier


def chemin_libre(cible: Path) -> Path:
    # Jamais écraser : "photo.jpg" -> "photo (1).jpg", "photo (2).jpg"...
    base, n = cible, 1
    while cible.exists():
        cible = base.with_name(f"{base.stem} ({n}){base.suffix}")
        n += 1
    return cible


def ranger(dossier: Path, fichier: Path, regles, ext_vers_dossier):
    """Déplace un fichier ; renvoie la destination, ou None s'il faut l'ignorer / réessayer."""
    if not fichier.is_file() or fichier.name in regles["ignorer"]:
        return None
    ext = fichier.suffix.lower()
    if ext in regles["en_cours"] or ext not in ext_vers_dossier:
        return None
    destination = dossier / ext_vers_dossier[ext]
    destination.mkdir(exist_ok=True)
    cible = chemin_libre(destination / fichier.name)
    try:
        os.rename(fichier, cible)  # échoue (sans rien perdre) si le fichier est encore ouvert ou existe déjà
    except OSError:
        return None
    return cible


def surveiller(dossier: Path, pause=2.0):
    regles, ext_vers_dossier = charger()
    deja_la = {p.name for p in dossier.iterdir()}  # fichiers présents au lancement : jamais touchés
    tailles = {}
    print(f"Surveillance de {dossier} (Ctrl+C pour arrêter)")
    while True:
        presents = list(dossier.iterdir())
        deja_la &= {p.name for p in presents}  # un fichier supprimé puis re-téléchargé redevient "nouveau"
        for p in presents:
            if p.name in deja_la or not p.is_file():
                continue
            taille = p.stat().st_size
            if tailles.get(p.name) != taille:  # attendre que la taille ne bouge plus entre deux passages
                tailles[p.name] = taille
                continue
            cible = ranger(dossier, p, regles, ext_vers_dossier)
            if cible:
                tailles.pop(p.name, None)
                print(f"{p.name} -> {cible.relative_to(dossier)}")
        time.sleep(pause)


if __name__ == "__main__":
    regles, _ = charger()
    chemin = sys.argv[1] if len(sys.argv) > 1 else os.path.expandvars(regles["dossier"])
    if not chemin or not Path(chemin).is_dir():
        sys.exit("Indique le dossier à surveiller dans regles.json (\"dossier\").")
    try:
        surveiller(Path(chemin))
    except KeyboardInterrupt:
        pass
