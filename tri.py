"""Surveille un dossier et range chaque nouveau fichier selon son extension."""
import json, os, queue, subprocess, sys, threading, time
from pathlib import Path

# En .exe : regles.json à côté de l'exe s'il existe, sinon la copie embarquée.
ICI = Path(sys.executable if getattr(sys, "frozen", False) else __file__).parent
CONFIG = ICI / "regles.json"
if not CONFIG.exists():
    CONFIG = Path(getattr(sys, "_MEIPASS", ICI)) / "regles.json"


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


def categorie(fichier: Path, regles, ext_vers_dossier):
    """Sous-dossier où ranger ce fichier, ou None s'il ne faut pas y toucher."""
    if not fichier.is_file() or fichier.name in regles["ignorer"]:
        return None
    ext = fichier.suffix.lower()
    if ext in regles["en_cours"] or ext not in ext_vers_dossier:
        return None
    # Firefox crée "film.mp4" vide à côté de "film.mp4.part" : attendre la fin.
    if any(fichier.with_name(fichier.name + e).exists() for e in regles["en_cours"]):
        return None
    return ext_vers_dossier[ext]


def apercu(dossier: Path):
    """Simulation : {fichier: catégorie} pour ce qui est déjà dans le dossier. Ne déplace rien."""
    regles, ext_vers_dossier = charger()
    return {p: c for p in dossier.iterdir() if (c := categorie(p, regles, ext_vers_dossier))}


def ranger(dossier: Path, fichier: Path, regles, ext_vers_dossier):
    """Déplace un fichier ; renvoie la destination, ou None s'il faut l'ignorer / réessayer."""
    nom = categorie(fichier, regles, ext_vers_dossier)
    if not nom:
        return None
    try:
        destination = dossier / nom
        destination.mkdir(exist_ok=True)
        cible = chemin_libre(destination / fichier.name)
        os.rename(fichier, cible)  # échoue (sans rien perdre) si le fichier est encore ouvert ou existe déjà
    except OSError:
        return None
    return cible


def surveiller(dossier: Path, pause=2.0, arret=None, signaler=print):
    """Boucle jusqu'à arret.set(). signaler(nom, destination) à chaque fichier rangé."""
    regles, ext_vers_dossier = charger()
    arret = arret or threading.Event()
    deja_la = {p.name for p in dossier.iterdir()}  # fichiers présents au lancement : jamais touchés
    tailles = {}
    while not arret.is_set():
        try:
            presents = list(dossier.iterdir())
        except OSError:  # dossier momentanément inaccessible : réessayer
            presents = []
        deja_la &= {p.name for p in presents}  # un fichier supprimé puis re-téléchargé redevient "nouveau"
        tailles = {k: v for k, v in tailles.items() if k in {p.name for p in presents}}
        for p in presents:
            if p.name in deja_la:
                continue
            try:
                if not p.is_file():
                    continue
                taille = p.stat().st_size
            except OSError:  # fichier disparu entre-temps
                continue
            if tailles.get(p.name) != taille:  # attendre que la taille ne bouge plus entre deux passages
                tailles[p.name] = taille
                continue
            cible = ranger(dossier, p, regles, ext_vers_dossier)
            if cible:
                tailles.pop(p.name, None)
                signaler(p.name, cible.relative_to(dossier))
        arret.wait(pause)


def fenetre(dossier: Path):
    import ctypes, tkinter as tk
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # texte net sur écrans haute résolution
    except Exception:
        pass

    FOND, CARTE, TEXTE, GRIS, VERT, ROUGE = "#16181d", "#20232a", "#e6e8ec", "#8b919c", "#3ecf8e", "#ef5f5f"
    racine = tk.Tk()
    racine.title("Tri des téléchargements")
    racine.geometry("680x440")
    racine.minsize(600, 300)
    racine.configure(bg=FOND)
    police = ("Segoe UI", 10)

    haut = tk.Frame(racine, bg=FOND)
    haut.pack(fill="x", padx=20, pady=(18, 8))
    tk.Label(haut, text="Tri des téléchargements", bg=FOND, fg=TEXTE, font=("Segoe UI Semibold", 15)).pack(anchor="w")
    tk.Label(haut, text=str(dossier), bg=FOND, fg=GRIS, font=police).pack(anchor="w")

    barre = tk.Frame(racine, bg=FOND)
    barre.pack(fill="x", padx=20, pady=8)
    etat = tk.Label(barre, bg=FOND, font=("Segoe UI Semibold", 11))
    etat.pack(side="left")
    bouton = tk.Button(barre, font=("Segoe UI Semibold", 10), relief="flat", bd=0, padx=18, pady=6,
                       fg=FOND, activeforeground=FOND, cursor="hand2")
    bouton.pack(side="right")
    tk.Button(barre, text="Ouvrir le dossier", font=police, relief="flat", bd=0, padx=14, pady=6,
              bg=CARTE, fg=TEXTE, activebackground="#2b2f38", activeforeground=TEXTE, cursor="hand2",
              command=lambda: os.startfile(dossier)).pack(side="right", padx=8)
    tk.Button(barre, text="Ranger l'existant…", font=police, relief="flat", bd=0, padx=14, pady=6,
              bg=CARTE, fg=TEXTE, activebackground="#2b2f38", activeforeground=TEXTE, cursor="hand2",
              command=lambda: ranger_existant()).pack(side="right")

    tk.Label(racine, text="Derniers fichiers rangés", bg=FOND, fg=GRIS, font=police).pack(anchor="w", padx=20, pady=(8, 4))
    liste = tk.Listbox(racine, bg=CARTE, fg=TEXTE, font=police, bd=0, highlightthickness=0, activestyle="none",
                       selectbackground="#2b2f38", selectforeground=TEXTE)
    liste.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    vide = "  Aucun fichier rangé pour l'instant."
    liste.insert("end", vide)
    liste.itemconfig(0, fg=GRIS)

    rangés = queue.Queue()
    chemins = []  # destination de chaque ligne, pour l'ouvrir au double-clic
    travail = {"arret": None}

    def demarrer():
        travail["arret"] = threading.Event()
        threading.Thread(target=surveiller, daemon=True,
                         args=(dossier, 2.0, travail["arret"], lambda n, c: rangés.put((n, c)))).start()
        etat.config(text="●  Surveillance active", fg=VERT)
        bouton.config(text="Arrêter", bg=ROUGE, activebackground=ROUGE, command=arreter)

    def ranger_existant():
        # Simulation d'abord, puis confirmation : rien ne bouge sans accord.
        from collections import Counter
        from tkinter import messagebox
        prevu = apercu(dossier)
        if not prevu:
            messagebox.showinfo("Ranger l'existant", "Rien à ranger.")
            return
        detail = "\n".join(f"  {n} → {c}" for c, n in Counter(prevu.values()).most_common())
        if not messagebox.askyesno("Ranger l'existant", f"{len(prevu)} fichier(s) seront déplacés :\n\n{detail}\n\n"
                                   "Rien n'est supprimé ni écrasé. Continuer ?"):
            return
        regles, ext_vers_dossier = charger()
        for f in prevu:
            if cible := ranger(dossier, f, regles, ext_vers_dossier):
                rangés.put((f.name, cible.relative_to(dossier)))

    def arreter():
        travail["arret"].set()
        etat.config(text="●  En pause", fg=GRIS)
        bouton.config(text="Démarrer", bg=VERT, activebackground=VERT, command=demarrer)

    def relever():
        while not rangés.empty():
            nom, cible = rangés.get()
            if not chemins:
                liste.delete(0)
            liste.insert(0, f"  {time.strftime('%H:%M')}   {nom}   →  {cible.parent}")
            chemins.insert(0, dossier / cible)
            if liste.size() > 200:
                liste.delete("end")
                chemins.pop()
        racine.after(500, relever)

    def ouvrir(_):
        i = liste.curselection()
        if i and i[0] < len(chemins) and chemins[i[0]].exists():
            subprocess.Popen(["explorer", f"/select,{chemins[i[0]]}"])  # montre le fichier dans l'Explorateur

    liste.bind("<Double-Button-1>", ouvrir)
    try:  # barre de titre sombre (Windows 10/11)
        racine.update()
        hwnd = ctypes.windll.user32.GetParent(racine.winfo_id())
        ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(ctypes.c_int(1)), 4)
    except Exception:
        pass
    demarrer()
    relever()
    racine.mainloop()


if __name__ == "__main__":
    regles, _ = charger()
    chemin = Path(sys.argv[1] if len(sys.argv) > 1 else os.path.expandvars(regles["dossier"]))
    if not chemin.is_dir():
        import tkinter.messagebox
        tkinter.messagebox.showerror("Tri des téléchargements", f"Dossier introuvable :\n{chemin}\n\nVérifie \"dossier\" dans regles.json.")
        sys.exit(1)
    fenetre(chemin)
