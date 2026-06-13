ASSETS — Mission Espace
=======================

Ce dossier contient les ressources statiques du jeu.

Structure :
-----------
assets/
├── wallpapers/         Fonds d'écran spatiaux à inclure dans le dépôt git.
│   └── .gitkeep       (dossier vide par défaut — les wallpapers sont copiés
│                        par les scripts d'installation depuis /usr/share/backgrounds/
│                        ou générés dynamiquement par Python si aucun n'est trouvé)
└── README.txt          Ce fichier.

Fonds d'écran (wallpapers)
--------------------------
Les images de fond d'écran NE SONT PAS committées dans le dépôt car :
  • Elles peuvent être volumineuses (JPEG/PNG haute résolution)
  • Elles sont disponibles sur la machine cible via /usr/share/backgrounds/

Lors de l'installation (setup/install.sh), les scripts :
  1. Cherchent des images dans /usr/share/backgrounds/linuxmint/ et /usr/share/backgrounds/
  2. En copient jusqu'à 6 dans /home/<joueur>/game/wallpapers/
  3. Si aucune image n'est trouvée, génèrent un PNG coloré via Python (stdlib uniquement)

Pour ajouter des wallpapers manuellement :
  Copiez vos images dans /home/romy/game/wallpapers/ et /home/oscar/game/wallpapers/
  (formats supportés : JPEG, PNG)
