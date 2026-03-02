# MonPanelLocal - Suivi d'Avancement et Historique (Changelog)

Ce document retrace l'historique de développement, les fonctionnalités ajoutées et l'architecture du projet afin de conserver un suivi propre.

---

## 👥 Version 4.0 - Gestion des Joueurs en Temps Réel (Actuelle)
**Date :** 02 Mars 2026
**Objectif :** Suivre les connexions et déconnexions des joueurs en direct et permettre leur modération rapide.

**Modifications Apportées :**
- **Parsing des Logs en Direct & Résilience (Hotfix)** (`server_manager.py`) : Ajout du module `re` pour intercepter les flux `joined the game` et `left the game` dans la sortie standard de Java, afin de recenser les joueurs dans un `set` Python. Une routine efface les codes couleurs ANSI invisibles injectés par PaperMC et la regex capture les joueurs Bedrock (`.` ou `*`).
- **Ajout de l'Onglet Joueurs** (`tab_players.py` & `main_window.py`) : Interface proposant un listing de boutons via un `CTkScrollableFrame` (Op, Kick, Ban) connectés au `stdin` du processus Java. Ajout d'un bouton de rafraîchissement manuel captant la commande `/list`.
- **Intégration Thread-Safe** (`main.py`) : L'événement de mise à jour `on_players_update_callback` transite proprement vers le processus principal via `.after(0)` pour éviter tout crash Tkinter.

---

## ☕ Version 3.0 - Runtimes Java Dynamiques
**Date :** 02 Mars 2026
**Objectif :** Télécharger et utiliser la bonne version de Java automatiquement selon la version du serveur (indépendant de la machine hôte).

**Modifications Apportées :**
- **Création du JavaManager** (`java_manager.py`) : Connexion à l'API [Adoptium V3](https://api.adoptium.net) pour trouver les binaires des JREs selon l'architecture (x64/arm) et l'OS (Windows/Mac/Linux).
- **Extraction Intelligente** : Les JREs `.zip` ou `.tar.gz` téléchargés sont extraits localement dans le dossier `/runtimes/java_X/` propre au panel.
- **Lancement Isolé** (`server_manager.py`) : Au démarrage, le panel détecte la version de Java requise (Java 8 pour <=1.16, Java 16 pour 1.17, Java 17 pour <=1.20.4, Java 21 pour >=1.20.5). S'il ne l'a pas, il la télécharge. Le démarrage du serveur utilise alors cet exécutable explicite au lieu du traditionnel `java` global du PC.

---

## 🛠️ Version 2.0 - Gestion Dynamique des Versions (Actuelle)
**Date :** 02 Mars 2026
**Objectif :** Intégrer la sélection et l'installation de n'importe quelle version de Minecraft supportée par PaperMC via leur API.

**Modifications Apportées :**
- **Ajout de l'API PaperMC complète** (`downloader.py`) : L'application récupère la liste complète des versions de Minecraft au lancement avec la bibliothèque `requests` dans un thread asynchrone.
- **Ajout d'un menu déroulant (OptionMenu)** (`tab_console.py`) : Un `CTkOptionMenu` a été ajouté au-dessus des contrôles pour choisir la version voulue.
- **Séparation des serveurs par version** (`server_manager.py`) : Au moment de l'installation, un dossier dédié `minecraft_server_[VERSION]/` est créé (par exemple `minecraft_server_1.20.4/`). Le `server.jar`, l'`eula.txt` et `server.properties` y sont isolés.
- **Système d'Installation intelligent** (`main_window.py` & `tab_console.py`) : Si la version sélectionnée n'est pas trouvée localement, le bouton "Démarrer" est caché et remplacé par un bouton "Installer". Une fois l'installation terminée via la nouvelle barre de progression (`CTkProgressBar`), le bouton "Démarrer" réapparaît.
- **Formulaire de Paramètres dynamique** (`config_manager.py` & `tab_settings.py`) : Le fichier lu est désormais toujours celui de la bonne version (par exemple `minecraft_server_1.19.4/server.properties`). Lorsque l'utilisateur change de version dans l'onglet Console, le formulaire de l'onglet Paramètres se met à jour en direct.

---

## 🏗️ Version 1.0 - Refactorisation et Architecture Propre
**Date :** 02 Mars 2026
**Objectif :** Transformer le script unique `app.py` en une architecture logicielle MVC/Modulaire robuste, séparant l'interface graphique du moteur de l'application.

**Création de l'Architecture :**
* `main.py` : Point d'entrée "Glue" de l'application. Initialise les objets et les injecte.
* **Le Core (Backend)** : Totalement agnostique de l'UI. Communique uniquement par des fonctions Callbacks.
  * `core/server_manager.py` : Gère le processus `java` enfant (subprocess) en tâche de fond. Redirige la sortie texte et gère les envois de commandes.
  * `core/downloader.py` : Module de téléchargement du serveur.
  * `core/config_manager.py` : Parse et modifie le fichier texte `server.properties` en évitant d'écraser les commentaires.
  * `core/system_monitor.py` : Fonctionne en asynchrone pour lire l'état du CPU et de la RAM via `psutil`.
* **L'UI (Frontend)** : N'importe aucune logique métier profonde et utilise `customtkinter`. Utilise `.after(0)` pour afficher les évènements venus du Backend en toute sécurité vis-à-vis des Threads Python.
  * `ui/main_window.py` : La fenêtre globale regroupant les onglets dans un `CTkTabview`.
  * `ui/tab_console.py` : L'onglet affichant les logs serveurs et l'envoi de commandes.
  * `ui/tab_settings.py` : Le formulaire pour modifier les settings d'un serveur Minecraft avec le `config_manager`.
  * `ui/widget_monitor.py` : La barre statique en bas d'écran gérant la progression RAM/CPU locale de la machine hôte.

---

## 🌱 Initialisation - Proof Of Concept
**Objectif Initial :** Créer un "Nitrado Local". Interface assombrie via `CustomTkinter`, lancement de java en sous-processus de manière non-bloquante avec `threading` et génération auto du fichier `eula.txt`.
