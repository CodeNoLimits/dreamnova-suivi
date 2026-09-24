# DreamNova · Portail des livraisons

Catalogue public : https://codenolimits.github.io/dreamnova-suivi/

Chaque projet a une page indépendante sous `projets/<id>/`, sans navigation vers les autres dossiers clients. Le site reste public : une URL difficile à deviner ne protège pas un document. Les pièces confidentielles, comptes, rapports internes et contenus sacrés non approuvés restent hors de ce dépôt.

## Publication

`status.json` est le manifeste public. `build_portal.py` génère l’accueil et les pages statiques. `assets/portal.css` et `assets/portal.js` gèrent présentation, recherche et filtres. Aucune dépendance de compilation.

```sh
python3 build_portal.py
node --check assets/portal.js
```

La supervision Astra est propriétaire du portail pendant le mandat du 24 septembre. La supervision planifiée effectue un dernier passage à 18:30 Jérusalem. Les responsables des projets lui transmettent liens et preuves, sans pousser simultanément dans ce dépôt.

Ensuite, `publish_status.py` permet une mise à jour bornée : vérification des URL HTTPS, reconstruction des pages, commit, push et vérification du manifeste ET de la révision HTML de l’accueil, de la fiche modifiée et du journal. `--proof` doit rester une preuve publique sans information privée.

```sh
python3 publish_status.py --id keren --status review --url https://keren-rabbi-israel-catalogue.vercel.app/ --summary 'Prototype du catalogue consultable.' --proof 'Catalogue et lecture mobile vérifiés.'
```

États : `available` = accès disponible ; `review` = version en revue. Le premier état ne certifie pas toutes les fonctions. Les paramètres historiques `live` et `working` restent des alias. Les identifiants valides se trouvent dans le manifeste.

## Médias

Les vidéos déjà publiques sont lues depuis leur hébergeur. Les MP4 GitHub Pages, de même origine que ce portail, ont un lien `download`. Les vidéos Woodeex restent sur leur salle de visionnage où le téléchargement est fourni par le même hébergeur. Ne pas dupliquer les gros masters uniquement pour ce portail.

La publication n’est confirmée qu’après contrôle de GitHub Pages, des pages dédiées et des fichiers téléchargeables. Les anciennes pages `handover/` restent présentes pour conserver les liens historiques.

## Fraîcheur et compte rendu

Le manifeste conserve uniquement les informations publiques approuvées. Son tableau `journal` alimente le compte rendu expurgé. Toute mise à jour reconstruit 14 pages avec la même révision et des assets versionnés. Une page ouverte contrôle cette révision toutes les 30 secondes quand elle est visible. Elle attend la diffusion du HTML correspondant avant de recharger ; lecture vidéo et saisie en cours sont préservées. Le bouton Actualiser permet de forcer la nouvelle version. Un réseau indisponible conserve les liens affichés. Cette vérification ne prétend pas que les agents ont publié un nouveau travail toutes les 30 secondes.

Les informations de projet doivent être validées avant leur ajout au manifeste. Les sources, communications, détails financiers et dossiers de brevets restent privés. La page 404 ramène au catalogue canonique.
