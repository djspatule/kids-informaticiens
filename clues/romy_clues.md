# Fichiers de jeu — Romy (Capitaine de l'Espace)

Ce document liste le contenu exact de chaque fichier que le script de setup
doit créer dans /home/romy/. Copier le contenu tel quel (encodage UTF-8).

---

## ~/Bureau/Fusée/message_1.txt

```
🚀✨ MESSAGE DE LA STATION SPATIALE ✨🚀
=========================================

Bonjour Capitaine Romy !

Félicitations ! Tu viens d'activer ton premier message spatial.

Ta fusée est prête à décoller, mais avant de partir dans les étoiles,
tu dois accomplir plusieurs missions importantes !

🌟 MISSION SUIVANTE :
Une étoile mystérieuse se cache quelque part dans ton ordinateur...
Cherche dans le dossier Étoiles qui se trouve dans ta Maison !

Bonne exploration, Capitaine ! 💫

— Le Centre de Contrôle Spatial 🛸
```

---

## ~/Étoiles/etoile.txt

```
⭐✨ TU AS TROUVÉ L'ÉTOILE ! BRAVO ! ✨⭐
==========================================

         *    .  *       .         *
    .  *    ✨   .    *    .   ✨
  *    .  *  ÉTOILE  *  .  *   .
    .  *    ✨   .    *    .   ✨
         *    .  *       .         *

Super Capitaine Romy ! Tu as trouvé l'étoile cachée !

🎨 MISSION SUIVANTE :
Ton vaisseau a besoin d'une belle décoration !
Change le fond d'écran de ton Bureau pour une image de l'espace.

👉 Comment faire :
   → Fais un clic droit sur le Bureau (là où il n'y a rien)
   → Choisis "Paramètres du Bureau"
   → Sélectionne une belle image de l'espace dans le dossier :
     /home/romy/game/wallpapers/

Rends ton vaisseau le plus beau de la galaxie ! 🌌🪐

— L'Étoile Polaire 🌟
```

---

## ~/Trouvailles/cle.txt

```
🔑 LA CLÉ DU TRÉSOR 🔑
========================

         🔑
        /|||
       / ||| 
      /  |||___
     (   |||   )
      \  |||---
       \ |||
        \|||
         ·

Tu as trouvé la Clé du Trésor, Capitaine Romy !

Mais attention... cette clé doit rejoindre son vaisseau !
Tu dois la déplacer dans le dossier Vaisseau pour qu'elle
soit en sécurité.

Une fois dans le Vaisseau, la clé révélera son secret final...

Continue tes missions courageusement ! 🚀💫

— Le Gardien des Trésors Spatiaux ⭐
```

---

## ~/Vaisseau/cle.txt

> Note : Ce fichier est la DESTINATION de mission_05 (déplacer cle.txt
> depuis ~/Trouvailles/ vers ~/Vaisseau/). Le setup script doit créer
> le fichier ~/Trouvailles/cle.txt avec le contenu ci-dessus.
> Après que l'enfant le déplace, il se retrouve ici avec le même contenu.
> La mission_08 demande à l'enfant de lire CE fichier dans ~/Vaisseau/.
> Aucun contenu supplémentaire à préparer — c'est le même fichier déplacé.

---

## Notes pour le setup script

- Créer le dossier ~/Bureau/Fusée/ (avec accent)
- Créer ~/Bureau/Fusée/message_1.txt
- Créer ~/Étoiles/ et ~/Étoiles/etoile.txt
- Créer ~/Mission/ (dossier vide)
- Créer ~/Trouvailles/ et ~/Trouvailles/cle.txt
- Créer ~/Vaisseau/ (dossier vide — cle.txt y arrive par le jeu)
- Créer ~/game/wallpapers/ avec des images .jpg/.png de l'espace
- Tous les fichiers doivent appartenir à l'utilisateur romy (chown romy:romy)
- Encodage UTF-8 obligatoire pour les accents et emojis
```
