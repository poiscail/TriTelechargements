"""Test sur un dossier temporaire : python test_tri.py"""
import tempfile, threading, time
from pathlib import Path
import tri

with tempfile.TemporaryDirectory() as d:
    d = Path(d)
    (d / "ancien.pdf").write_text("déjà là")
    (d / "Outils").mkdir()
    (d / "Documents").mkdir()
    (d / "Documents" / "rapport.pdf").write_text("existant")
    threading.Thread(target=tri.surveiller, args=(d, 0.2), daemon=True).start()
    time.sleep(0.5)
    (d / "photo.JPG").write_text("x")
    (d / "rapport.pdf").write_text("nouveau")
    (d / "film.mp4.crdownload").write_text("en cours")
    (d / "inconnu.xyz").write_text("x")
    (d / "setup.exe").write_text("x")
    time.sleep(1.5)
    assert (d / "ancien.pdf").exists()
    assert (d / "Images" / "photo.JPG").exists()
    assert (d / "Documents" / "rapport.pdf").read_text() == "existant"
    assert (d / "Documents" / "rapport (1).pdf").read_text() == "nouveau"
    assert (d / "film.mp4.crdownload").exists()
    assert (d / "inconnu.xyz").exists()
    assert (d / "Installateurs" / "setup.exe").exists()
    assert (d / "Outils").is_dir()
    (d / "film.mp4.crdownload").rename(d / "film.mp4")  # fin du téléchargement
    time.sleep(1.5)
    assert (d / "Vidéos" / "film.mp4").exists()
print("OK")
