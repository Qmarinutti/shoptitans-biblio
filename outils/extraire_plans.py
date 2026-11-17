"""Extrait le catalogue des plans depuis playshoptitans.com (pages Next.js, noms FR + EN).

Sortie : ../data/plans.json et ../supabase/02_plans.sql
Usage  : python -I extraire_plans.py
A relancer après une mise à jour du jeu : le SQL fait un upsert, rien n'est perdu.
"""
import json, re, time, urllib.request, pathlib

BASE = "https://playshoptitans.com"

# (catégorie, code page, libellé FR du type) dans l'ordre d'affichage du site officiel
TYPES = [
    ("Armes", "weapons/ws", "Épées"), ("Armes", "weapons/wa", "Haches"), ("Armes", "weapons/wd", "Dagues"),
    ("Armes", "weapons/wm", "Masses"), ("Armes", "weapons/wp", "Lances"), ("Armes", "weapons/wb", "Arcs"),
    ("Armes", "weapons/ww", "Baguettes"), ("Armes", "weapons/wt", "Bâtons"), ("Armes", "weapons/wg", "Fusils"),
    ("Armes", "weapons/wc", "Arbalètes"), ("Armes", "weapons/wi", "Instruments"), ("Armes", "weapons/w2", "Armes double"),
    ("Armes", "weapons/wy", "Catalyseurs"), ("Armes", "weapons/wh", "Faux"),
    ("Armures", "armor/ah", "Armures lourdes"), ("Armures", "armor/am", "Armures légères"), ("Armures", "armor/al", "Habits"),
    ("Armures", "armor/hh", "Casques"), ("Armures", "armor/hm", "Chapeaux de roublard"), ("Armures", "armor/hl", "Chapeaux de magicien"),
    ("Armures", "armor/hk", "Masques"), ("Armures", "armor/gh", "Gantelets"), ("Armures", "armor/gl", "Brassards"),
    ("Armures", "armor/bh", "Bottes"), ("Armures", "armor/bl", "Chaussures"),
    ("Accessoires", "accessories/uh", "Herbes médicinales"), ("Accessoires", "accessories/up", "Potions"),
    ("Accessoires", "accessories/us", "Sorts"), ("Accessoires", "accessories/xs", "Boucliers"),
    ("Accessoires", "accessories/xr", "Anneaux"), ("Accessoires", "accessories/xa", "Amulettes"),
    ("Accessoires", "accessories/xc", "Capes"), ("Accessoires", "accessories/xf", "Familiers"),
    ("Accessoires", "accessories/xx", "Chants d'aura"), ("Accessoires", "accessories/xq", "Carquois"),
    ("Accessoires", "accessories/xi", "Idoles"), ("Accessoires", "accessories/fm", "Plats"),
    ("Accessoires", "accessories/fd", "Desserts"),
    ("Pierres", "stones/xu", "Pierres runiques"), ("Pierres", "stones/xm", "Pierres de lune"),
    ("Enchantements", "enchantments/fire", "Feu"), ("Enchantements", "enchantments/water", "Eau"),
    ("Enchantements", "enchantments/earth", "Terre"), ("Enchantements", "enchantments/air", "Air"),
    ("Enchantements", "enchantments/light", "Lumière"), ("Enchantements", "enchantments/dark", "Ténèbres"),
    ("Enchantements", "enchantments/gold", "Or"), ("Enchantements", "enchantments/spirit", "Esprits"),
]

ICI = pathlib.Path(__file__).resolve().parent
RACINE = ICI.parent


def page(path):
    req = urllib.request.Request(BASE + path, headers={"User-Agent": "Mozilla/5.0 (biblio-plans)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        html = r.read().decode("utf-8")
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    return json.loads(m.group(1))["props"]["pageProps"]


def sql_txt(v):
    if v is None:
        return "null"
    if isinstance(v, int):
        return str(v)
    return "'" + str(v).replace("'", "''") + "'"


def main():
    plans, vus = [], set()
    for ordre, (cat, chemin, type_fr) in enumerate(TYPES):
        code = chemin.split("/")[1]
        en = page("/blueprints/" + chemin)
        fr = page("/fr/blueprints/" + chemin)
        items = en.get("items") or []
        if isinstance(items, dict):
            items = list(items.values())
        n = 0
        for pos, it in enumerate(items):
            uid = it.get("uid")
            if not uid or uid in vus:
                continue
            if cat != "Enchantements" and it.get("type") not in (None, code):
                continue
            vus.add(uid)
            n += 1
            plans.append({
                "id": uid,
                "nom_fr": fr["texts"].get(uid + "_name") or en["texts"].get(uid + "_name") or uid,
                "nom_en": en["texts"].get(uid + "_name") or uid,
                "categorie": cat,
                "type_code": code,
                "type_nom": type_fr,
                "ordre_type": ordre,
                "ordre": pos,
                "tier": it.get("tier"),
                "origine": it.get("excl"),
            })
        print(f"{chemin:22s} {n:4d}")
        time.sleep(0.4)

    (RACINE / "data").mkdir(exist_ok=True)
    (RACINE / "data" / "plans.json").write_text(json.dumps(plans, ensure_ascii=False, indent=1), encoding="utf-8")

    cols = ["id", "nom_fr", "nom_en", "categorie", "type_code", "type_nom", "ordre_type", "ordre", "tier", "origine"]
    lignes = ",\n".join("(" + ",".join(sql_txt(p[c]) for c in cols) + ")" for p in plans)
    sql = (f"insert into public.plans ({','.join(cols)}) values\n{lignes}\n"
           "on conflict (id) do update set " + ", ".join(f"{c}=excluded.{c}" for c in cols[1:]) + ";\n")
    (RACINE / "supabase").mkdir(exist_ok=True)
    (RACINE / "supabase" / "02_plans.sql").write_text(sql, encoding="utf-8")
    print("TOTAL", len(plans))


if __name__ == "__main__":
    main()
