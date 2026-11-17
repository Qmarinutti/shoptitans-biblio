# Bibliothèque de plans — Shop Titans

Site de guilde : chaque joueur coche les plans qu'il possède (vert = je l'ai, gris = je ne l'ai pas)
et peut consulter la bibliothèque des autres membres ou voir « qui a ce plan ».

- **Hébergement** : GitHub Pages (page statique `index.html`)
- **Comptes + base** : Supabase, projet `shoptitans-biblio` (organisation « Shop Titans », plan Free)
  - URL : `https://xiwfkyjqxjfrvfvrzcuf.supabase.co`
  - Clé publique (publishable) dans `index.html` : sans danger, la sécurité est assurée par les règles RLS
- **Catalogue** : 1 670 plans extraits de playshoptitans.com (noms FR + EN), images chargées depuis ce site

## Fichiers

| Fichier | Rôle |
|---|---|
| `index.html` | Le site (HTML/CSS/JS, supabase-js depuis jsDelivr) |
| `data/plans.json` | Catalogue utilisé par le site |
| `supabase/01_schema.sql` | Tables, fonctions, règles de sécurité |
| `supabase/02_plans.sql` | Remplissage / mise à jour du catalogue (upsert) |
| `outils/extraire_plans.py` | Régénère `plans.json` + `02_plans.sql` depuis le site officiel |
| `outils/serveur_local.py` | Serveur de test sur http://localhost:8765 |

## Administration

- **Changer le code de guilde** (SQL Editor) :
  `update public.config_privee set valeur = 'NOUVEAU-CODE' where cle = 'code_guilde';`
- **Exclure un joueur** :
  `update public.profils set membre = false where pseudo = 'Pseudo';`
- **Nouveaux plans après une MAJ du jeu** : `python -I outils/extraire_plans.py`, puis exécuter
  `supabase/02_plans.sql` dans le SQL Editor et pousser `data/plans.json`.
- **Pause Supabase** : un projet gratuit inactif 7 jours est mis en pause → le relancer depuis le dashboard
  (le workflow `.github/workflows/reveil.yml` l'appelle 2 fois par semaine pour l'éviter).
