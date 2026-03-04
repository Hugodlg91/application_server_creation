# MonPanelLocal - Suivi d'Avancement et Historique (Changelog)

Ce document retrace l'historique de développement, les fonctionnalités ajoutées et l'architecture du projet afin de conserver un suivi propre.

---

## 🎨 Version 6.2 - Améliorations de Confort (Actuelle)
**Date :** 04 Mars 2026
**Objectif :** Améliorer l'ergonomie de l'interface sans créer de nouveaux fichiers : historique de commandes, console colorée et planificateur de messages automatiques.

**Modifications Apportées :**
- **Historique des commandes** (`ui/tab_console.py`) : Les commandes envoyées sont mémorisées (50 max). Navigation avec les flèches ↑/↓ sur le champ de saisie, retour à ligne vide avec la flèche bas en bas de l'historique.
- **Console colorée** (`ui/tab_console.py`) : Les lignes de log sont colorisées via les tags natifs du widget `Text` interne (`_textbox`). Rouge pour les erreurs (`ERROR`, `[Erreur]`), jaune pour les avertissements (`WARN`/`WARNING`), bleu clair pour les messages système (`[Système]`, `[Bore]`, `[Java]`), gris clair pour les logs standards.
- **Planificateur Auto-Broadcast** (`core/server_manager.py` + `ui/tab_settings.py` + `ui/main_window.py`) : Nouveau `start_scheduler(message, interval_minutes)` dans `ServerManager` — thread daemon avec `time.sleep` qui envoie `say {message}` périodiquement si le serveur tourne. Arrêt via `stop_scheduler()`. Section UI dédiée `📢 Planificateur de Messages` dans l'onglet Paramètres : champ de message, menu d'intervalle (5/10/15/30/60 min), switch d'activation.

---

## ⚙️ Version 6.1 - Éditeur de Performances
**Date :** 04 Mars 2026
**Objectif :** Permettre à l'utilisateur de contrôler la RAM allouée au serveur et d'activer les optimisations Aikar Flags directement depuis l'interface, sans redémarrer l'application.

**Modifications Apportées :**
- **Nouveau système de persistance** (`core/config_manager.py` + `panel_config.json`) : Ajout de `load_performance_config()` et `save_performance_config(ram_mb, aikar_flags)`. La config est stockée dans `panel_config.json` à la racine de `MonPanelLocal/`. La lecture/écriture fusionne proprement avec les clés existantes (ex : token ngrok) sans les écraser.
- **Démarrage dynamique du serveur** (`core/server_manager.py`) : La signature de `start_server()` accepte désormais `aikar_flags=False`. En mode Aikar, 15 flags JVM G1GC optimisés remplacent les simples `-Xms`/`-Xmx`. Un message de log indique la configuration utilisée au démarrage : `[Système] Démarrage avec X Mo RAM | Aikar Flags : Activés/Désactivés`.
- **Section UI "Performances"** (`ui/tab_settings.py`) : Ajout d'un bloc visuel séparé `⚙️ Performances du Serveur` dans l'onglet Paramètres, contenant un `CTkOptionMenu` pour la RAM (512/1024/2048/4096/6144/8192 Mo), un `CTkSwitch` pour les Aikar Flags avec description en gris, un bouton de sauvegarde et un message de confirmation vert/rouge. Les valeurs sont pré-remplies depuis `panel_config.json` au chargement.
- **Câblage des dépendances** (`ui/main_window.py`) : Injection des callbacks `load_performance_config` et `save_performance_config` dans `TabSettings`. `_action_start` lit la config perf avant chaque démarrage du serveur.

---

## 🌐 Version 6.0 - Tunneling avec Bore
**Date :** 04 Mars 2026
**Objectif :** Rendre le serveur Minecraft accessible depuis Internet sans configuration de routeur locale (Plug & Play).

**Modifications Apportées :**
- **Nouveau Backend Automatisé** (`core/bore_manager.py`) : Téléchargement automatique de la dernière release de Bore en Rust depuis l'API GitHub, avec compatibilité multiplateforme Windows/Mac/Linux (x86 et arm). L'exécutable est enregistré dans `runtimes/bore/`.
- **Lancement et Parsing IP** : Lancement asynchrone du tunnel vers `bore.pub`. Interception automatique du port distant alloué dynamiquement par expressions régulières (`re`).
- **Interface Utilisateur Simplifiée** (`ui/tab_console.py` & `ui/main_window.py`) : Remplacement de l'outil précédent par un bouton unique "🌐 Rendre Public (Bore)" avec affichage immédiat en lecture seule de l'IP publique à communiquer aux joueurs.

---

## 🌐 Version 5.1 - Tunneling Local "Plug & Play" avec Playit.gg
**Date :** 02 Mars 2026
**Objectif :** Remplacer ngrok (limité par les règles d'authentification) par Playit.gg afin de rendre le serveur Minecraft accessible publiquement de manière totalement "Plug & Play", sans aucune configuration de compte requise.

**Modifications Apportées :**
- **Nouveau Backend Tunneling** (`core/playit_manager.py`) : Implémentation du `PlayitManager`. Ce module télécharge intelligemment l'exécutable natif `playit` depuis GitHub selon l'OS (Windows, Linux, macOS) et l'architecture (x86_64, aarch64). Il exécute ensuite ce processus en arrière-plan (daemon) et intercepte sa sortie standard en continu.
- **Récupération de l'IP Automatique par Regex** : Un parser de logs interprète l'output de `playit` pour y extraire automatiquement en cours de route l'URL de réclamation (pour lier le tunnel à son compte si on le souhaite) ainsi que l'adresse IP de jeu allouée publiquement.
- **Intégration Interface** (`ui/tab_console.py`) : Remplacement du bouton tunnel par "🌐 Activer Playit.gg". L'interface injecte deux nouveaux champs textuels (`entry_claim_link` et `entry_playit_ip`) affichés dynamiquement selon les événements expédiés par le backend via `.after(0)`.
- **Couplage Global et Extinction Propre** (`ui/main_window.py` & `main.py`) : À la fermeture de la fenêtre de l'application, un appel de fin est garanti (`playit_manager.stop()`) pour tuer silencieusement le sous-processus `playit` orphelin de son processus parent.

---

## 🧩 Version 5.0 - Gestionnaire de Plugins Modrinth
**Date :** 02 Mars 2026
**Objectif :** Intégrer la recherche, le téléchargement et l'installation de plugins Minecraft depuis l'API Modrinth directement via l'interface du panel.

**Modifications Apportées :**
- **Nouveau Backend Modrinth** (`core/plugin_manager.py`) : Création de la classe `PluginManager` pour interroger l'API distante (`/v2/search` pour la recherche de plugins `paper`, `/v2/project/...` pour l'obtention de l'URL du fichier `.jar` compatible avec la version actuellement sélectionnée). Le téléchargement s'effectue de manière ciblée dans le dossier `plugins/` du serveur courant.
- **Ajout de l'Onglet Plugins** (`ui/tab_plugins.py` & `ui/main_window.py`) : Nouvelle interface graphique proposant une barre de recherche. L'affichage des résultats s'effectue dynamiquement sous forme de "cartes" interactives (titre, description, bouton d'installation) dans une zone défilante (`CTkScrollableFrame`). Intégration d'une barre de progression fluide pour le suivi des téléchargements.
- **Architecture Thread-Safe et Asynchrone** (`main.py` & `plugin_manager.py`) : Les longues requêtes HTTP (recherche sur l'API et streaming des fichiers `.jar`) s'exécutent de façon non-bloquante via `threading.Thread(daemon=True)`. La communication avec l'interface graphique (pour injecter les cartes de résultats ou mettre à jour la jauge de progression) s'opère en toute sécurité dans l'UI Thread via des callbacks utilisant `after(0)`. Le module `core` reste ainsi strictement séparé de la librairie visuelle `customtkinter`.

---

## 👥 Version 4.0 - Gestion des Joueurs en Temps Réel
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
