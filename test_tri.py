"""Test sur un dossier temporaire : python test_tri.py"""
import tempfile, threading, time
from pathlib import Path
import tri

with tempfile.TemporaryDirectory() as d:
    d = Path(d)
    (d / "ancien.pdf").write_text("déjà là")
    (d / "Projet").mkdir()
    (d / "Cours").mkdir()
    (d / "Cours" / "cours.pdf").write_text("x")
    (d / "Documents").mkdir()
    (d / "Documents" / "rapport.pdf").write_text("existant")
    (d / "Archives").write_text("fichier qui porte le nom d'une catégorie")
    ranges, arret = [], threading.Event()
    t = threading.Thread(target=tri.surveiller, args=(d, 0.2, arret, lambda n, c: ranges.append(n)), daemon=True)
    t.start()
    time.sleep(0.5)
    (d / "photo.JPG").write_text("x")
    (d / "rapport.pdf").write_text("nouveau")
    (d / "film.mp4.crdownload").write_text("en cours")
    (d / "musique.mp3").write_text("")  # Firefox : fichier vide + .part
    (d / "musique.mp3.part").write_text("en cours")
    (d / "inconnu.xyz").write_text("x")
    (d / "setup.exe").write_text("x")
    (d / "copie.zip").write_text("x")
    time.sleep(1.5)
    assert t.is_alive()  # "Archives" bloque copie.zip sans faire planter la boucle
    assert (d / "ancien.pdf").exists()
    assert (d / "Images" / "photo.JPG").exists()
    assert (d / "Documents" / "rapport.pdf").read_text() == "existant"
    assert (d / "Documents" / "rapport (1).pdf").read_text() == "nouveau"
    assert (d / "film.mp4.crdownload").exists()
    assert (d / "musique.mp3").exists() and not (d / "Musique").exists()
    assert (d / "inconnu.xyz").exists() and (d / "copie.zip").exists()
    assert (d / "Installateurs" / "setup.exe").exists()
    assert (d / "Projet").is_dir() and (d / "Cours" / "cours.pdf").exists()
    (d / "film.mp4.crdownload").rename(d / "film.mp4")  # fin des téléchargements
    (d / "musique.mp3").unlink()
    (d / "musique.mp3.part").rename(d / "musique.mp3")
    time.sleep(1.5)
    assert (d / "Vidéos" / "film.mp4").exists()
    assert (d / "Musique" / "musique.mp3").read_text() == "en cours"
    assert set(ranges) == {"photo.JPG", "rapport.pdf", "setup.exe", "film.mp4", "musique.mp3"}
    arret.set()
    t.join(1)
    assert not t.is_alive()

# Simulation + rangement de l'existant : l'aperçu ne déplace rien.
with tempfile.TemporaryDirectory() as d:
    d = Path(d)
    (d / "Projet").mkdir()
    for n in ["a.pdf", "b.png", "c.xyz", "d.zip.crdownload"]:
        (d / n).write_text("x")
    prevu = tri.apercu(d)
    assert {p.name: c for p, c in prevu.items()} == {"a.pdf": "Documents", "b.png": "Images"}
    assert (d / "a.pdf").exists() and not (d / "Documents").exists()
print("OK")
