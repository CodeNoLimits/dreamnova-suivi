# DreamNova · page des projets

Page publique : https://codenolimits.github.io/dreamnova-suivi/

Le navigateur recharge `status.json` toutes les 30 secondes. Après chaque changement vérifié, l'agent responsable publie son état avec `publish_status.py`. Le script contrôle que les URL publiques répondent sans mur de connexion, pousse la modification sur GitHub Pages puis attend que la nouvelle version soit servie. Le délai normal de publication est d'environ une minute ; il ne faut pas annoncer le lien avant le message `PUBLISHED`.

```sh
python3 publish_status.py --id keren --status live \
  --url https://exemple.vercel.app/ \
  --summary 'Description courte du résultat consultable' \
  --proof 'Rendu mobile et ordinateur vérifié ; parcours testé' \
  --handover https://exemple.vercel.app/passation/
```

Identifiants : `dreamnova-classic`, `dreamnova-world`, `keren`, `woodeex`, `suno-cours`, `reels`. Les mises à jour sans lien restent en état `working`. Le dépôt est public : exclure secrets, coordonnées privées, contenu client confidentiel et diagnostics internes.
