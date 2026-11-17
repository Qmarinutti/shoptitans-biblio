"""Génère les icônes de l'appli (PWA Android) : icons/icon-192.png, icon-512.png, maskable-512.png
Usage : python outils/generer_icones.py   (nécessite Pillow : python -m pip install --user pillow)"""
import pathlib
from PIL import Image, ImageDraw

RACINE = pathlib.Path(__file__).resolve().parent.parent
FOND = (20, 22, 31)
OR = (240, 193, 75)
OR_FONCE = (176, 132, 36)
VERT = (62, 207, 110)


def dessiner(taille, marge):
    s = 4 * taille  # super-échantillonnage pour des bords lisses
    im = Image.new("RGB", (s, s), FOND)
    d = ImageDraw.Draw(im)
    z = s * (1 - 2 * marge)          # zone utile
    o = s * marge
    X = lambda v: o + v * z
    # parchemin
    d.rounded_rectangle([X(.18), X(.16), X(.82), X(.84)], radius=z * .06, fill=OR)
    d.rounded_rectangle([X(.12), X(.10), X(.88), X(.22)], radius=z * .06, fill=OR_FONCE)
    d.rounded_rectangle([X(.12), X(.78), X(.88), X(.90)], radius=z * .06, fill=OR_FONCE)
    # lignes de plan
    for i, y in enumerate((.32, .44, .56)):
        d.rounded_rectangle([X(.28), X(y), X(.62 if i != 1 else .56), X(y + .05)], radius=z * .02, fill=FOND)
    # coche verte
    w = int(z * .075)
    d.line([(X(.48), X(.66)), (X(.60), X(.76)), (X(.80), X(.50))], fill=VERT, width=w, joint="curve")
    return im.resize((taille, taille), Image.LANCZOS)


def main():
    dossier = RACINE / "icons"
    dossier.mkdir(exist_ok=True)
    dessiner(192, .06).save(dossier / "icon-192.png")
    dessiner(512, .06).save(dossier / "icon-512.png")
    dessiner(512, .16).save(dossier / "maskable-512.png")   # zone sûre Android (cercle)
    print("ok")


if __name__ == "__main__":
    main()
