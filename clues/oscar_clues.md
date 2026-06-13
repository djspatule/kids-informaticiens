# Fichiers de jeu — Oscar (Commandant de l'Espace)

Ce document liste le contenu exact de chaque fichier que le script de setup
doit créer dans /home/oscar/. Copier le contenu tel quel (encodage UTF-8).

---

## ~/Bureau/Mission_Spatiale/ordre_01.txt

```
📡 ORDRE DE MISSION N°01 📡
==============================
CLASSIFICATION : COMMANDANT
DESTINATAIRE   : Oscar
DATE           : 2026-06-13
==============================

Commandant Oscar,

Bienvenue à bord de la Station Spatiale Gamma-7.
Ton expertise est requise pour plusieurs missions critiques.

📋 RÉSUMÉ DES OPÉRATIONS :
   1. Notre scanner a détecté une planète non identifiée dans le secteur 4.
      → Identifie-la et mets à jour notre base de données (dossier Planètes).

   2. Le catalogue planétaire est en désordre.
      → Classe les planètes dans les bons dossiers (Intérieures / Extérieures).

   3. Des fichiers secrets protègent nos codes d'accès.
      → Trouve et lis le fichier caché dans ta Base_Spatiale.

   4. Tu devras maîtriser le Terminal pour les transmissions finales.

🚀 Commence par la mission 2 : identifier la planète inconnue !
   Rends-toi dans ton dossier Planètes...

Bonne chance, Commandant. L'humanité compte sur toi.

— Général Kosmos, Quartier Général Spatial 🌌
```

---

## ~/Planètes/planete_inconnue.txt

```
🔭 RAPPORT DE DÉTECTION — PLANÈTE INCONNUE 🔭
================================================
STATUT : NON IDENTIFIÉE
SECTEUR : 4-ALPHA
DISTANCE DU SOLEIL : 1,52 UA (unités astronomiques)
================================================

Données du scanner :
  → Couleur de surface : rouge-orangé
  → Atmosphère : CO2 (95%), Azote (3%)
  → Lunes détectées : 2 (Phobos et Deimos)
  → Température moyenne : -63°C
  → Durée du jour : 24h 37min

⚠️ ANALYSE EN ATTENTE :
Ces caractéristiques correspondent à une planète rocheuse
du système solaire intérieur.

Indice : On l'appelle parfois la "planète rouge"...

🔍 MISSION : Renomme ce fichier avec le bon nom de la planète !
   (remplace planete_inconnue.txt par le nom correct)

— Système d'Analyse Automatique ARES-7 🤖
```

---

## ~/Planètes/venus.txt

```
🌍 FICHE PLANÈTE : VÉNUS 🌍
=============================
TYPE    : Planète intérieure (proche du Soleil)
ORDRE   : 2ème planète du système solaire
=============================

🌡️ Faits extraordinaires sur Vénus :
   • C'est la planète LA PLUS CHAUDE du système solaire (465°C !)
   • Pourtant elle est plus loin du Soleil que Mercure !
   • Son atmosphère épaisse retient la chaleur comme une serre.
   • Une journée sur Vénus dure plus longtemps qu'une année vénusienne !
   • Elle tourne dans le sens contraire des autres planètes.

📍 CLASSEMENT : Vénus est une planète INTÉRIEURE.
   → Elle doit être rangée dans le dossier Intérieures/

— Archives Cosmiques 🪐
```

---

## ~/Planètes/jupiter.txt

```
🪐 FICHE PLANÈTE : JUPITER 🪐
================================
TYPE    : Planète extérieure (géante gazeuse)
ORDRE   : 5ème planète du système solaire
================================

⚡ Faits extraordinaires sur Jupiter :
   • C'est la plus grande planète du système solaire !
   • Elle est si grande qu'on pourrait y mettre 1300 Terres.
   • Sa Grande Tache Rouge est une tempête géante qui dure depuis 400 ans !
   • Elle possède au moins 95 lunes connues.
   • Un jour sur Jupiter ne dure que 10 heures (rotation ultra-rapide !).

📍 CLASSEMENT : Jupiter est une planète EXTÉRIEURE.
   → Elle doit être rangée dans le dossier Extérieures/

— Archives Cosmiques 🪐
```

---

## ~/Planètes/mars.txt

> Note : Ce fichier n'existe pas au départ — c'est le fichier
> planete_inconnue.txt RENOMMÉ par l'enfant lors de la mission_02.
> Son contenu final sera celui de planete_inconnue.txt ci-dessus,
> simplement avec un nouveau nom. Aucune création séparée nécessaire.

---

## ~/Base_Spatiale/.code_secret

```
╔══════════════════════════════════════╗
║   🔐 FICHIER CLASSIFIÉ — NIVEAU 5   ║
╚══════════════════════════════════════╝

ACCÈS RESTREINT AU COMMANDANT AUTORISÉ

Félicitations, Commandant Oscar.
Tu as découvert ce fichier caché. Peu de gens savent
que les fichiers commençant par un point (.) sont
invisibles dans Linux !

📌 RAPPEL TECHNIQUE :
   → Dans Linux, tout fichier nommé .quelquechose est caché.
   → Pour les voir : appuie sur Ctrl+H dans le gestionnaire
     de fichiers, ou utilise ls -a dans le Terminal.

🔐 FRAGMENT DE CODE SECRET :
   Première partie  : COSMOS
   (La suite sera révélée quand tu auras accompli toutes les missions...)

🚀 PROCHAINE ÉTAPE :
   Maîtrise le Terminal ! Tu en auras besoin pour les
   transmissions finales de la station.
   → Mission suivante : ouvre un Terminal et utilise la commande ls

— Système de Sécurité SIGMA-9 🛡️
```

---

## Notes pour le setup script

- Créer ~/Bureau/Mission_Spatiale/ et ~/Bureau/Mission_Spatiale/ordre_01.txt
- Créer ~/Planètes/ avec les fichiers :
    - planete_inconnue.txt  (sera renommé en mars.txt par l'enfant)
    - venus.txt             (sera déplacé vers Intérieures/ par l'enfant)
    - jupiter.txt           (sera déplacé vers Extérieures/ par l'enfant)
    - Intérieures/          (sous-dossier vide — destination venus.txt)
    - Extérieures/          (sous-dossier vide — destination jupiter.txt)
- Créer ~/Base_Spatiale/ et ~/Base_Spatiale/.code_secret
- Créer ~/Mission_Journal/ (dossier vide)
- Créer ~/Transmissions/ (dossier vide)
- Créer ~/game/wallpapers/ avec des images .jpg/.png de l'espace
- Tous les fichiers doivent appartenir à l'utilisateur oscar (chown oscar:oscar)
- Encodage UTF-8 obligatoire pour les accents et emojis
- Le fichier .code_secret doit avoir le point initial (fichier caché Linux)
```
