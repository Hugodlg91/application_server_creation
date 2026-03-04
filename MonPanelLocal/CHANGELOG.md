# MonPanelLocal - Changelog

Ce document retrace l'historique de développement, les fonctionnalités ajoutées et l'architecture du projet.

---

## Version 8.8 - Fix ScrollableDropdown + Compaction barre de contrôles (Actuelle)
**Date :** 04 Mars 2026

**Bug** (`ui/widgets/scrollable_dropdown.py`) : La correction v8.2.1 (guard `is`) ne fonctionnait pas. En Python 3, les bound methods créent un nouvel objet à chaque accès → `cmd is not self._open_popup` est toujours `True`. De plus, `CTkButton` stocke également sa commande interne dans `self._command`, écrasant notre callback utilisateur après `super().__init__()`.
**Correctif** : Renommage de `self._command` en `self._on_select` pour éviter le conflit de nom avec `CTkButton`. Suppression de la garde complexe dans `configure()` — quand `command` est passé depuis l'extérieur, c'est toujours le callback utilisateur.

**Compaction** (`ui/tab_console.py`) : La barre de contrôles avait une hauteur non maîtrisable car `CTkOptionMenu` impose une hauteur minimale interne ignorant `height=`. Correctif : `height=42` sur `frame_controls` + `grid_propagate(False)` + `grid_rowconfigure(0, weight=1)` pour centrer les widgets verticalement dans la hauteur fixe. Tous les `pady` internes réduits à `0`.

---

## Version 8.7 - UI feedback fermeture élégante
**Date :** 04 Mars 2026

**Fonctionnalité** (`main.py`) : Quand `on_closing()` détecte le serveur actif :
- Désactivation immédiate du bouton WM (`protocol("WM_DELETE_WINDOW", lambda: None)`) pour empêcher le double-clic
- Titre de fenêtre changé en `"MonPanelLocal — Arrêt en cours..."`
- Message `"[Système] Arrêt du serveur en cours, veuillez patienter..."` affiché dans la console
- Fermeture appelée via `_final_close` une fois le thread `process.wait(timeout=30)` terminé

---

## Version 8.6 - Fermeture propre par attente réelle du processus
**Date :** 04 Mars 2026

**Correctif** (`main.py`) : Remplacement du délai fixe `app.after(3000, ...)` (3 secondes arbitraires pouvant corrompre une map en cours de sauvegarde) par un thread daemon appelant `server_manager.process.wait(timeout=30)`. La fenêtre reste ouverte jusqu'à la fin effective du processus Java, avec un timeout de sécurité à 30 secondes.

---

## Version 8.5 - Persistance du type de serveur
**Date :** 04 Mars 2026

**Fonctionnalité** (`core/config_manager.py`, `ui/main_window.py`) : Le type de serveur sélectionné (PaperMC / Vanilla / Fabric) est maintenant sauvegardé dans `panel_config.json` et restauré au redémarrage de l'application.
- Ajout de `load_server_type()` et `save_server_type(server_type)` dans `ConfigManager` (lecture/écriture fusionnée avec les autres clés de `panel_config.json`)
- `_initialize_app()` lit le type sauvegardé et pré-sélectionne le menu
- `_action_type_change()` sauvegarde à chaque changement

---

## Version 8.4 - Suppression des emojis + corrections bugs (5)
**Date :** 04 Mars 2026

**Emojis** : Tous les emojis vrais (`🌐👥🧩⛏🚀💾📢🔍`) supprimés ou remplacés par des symboles Unicode sûrs (`↓ × ↻ ▶ ■ ● ◉ ›`). Logos emoji dans `_make_section_card()`, `_show_empty_state()`, `_show_prompt_state()` supprimés. Icônes de `TabBar` réduites à du texte simple.

**Bug 1** (`ui/tab_console.py`) : `CTkTextbox(state="disabled")` silençait tous les appels `.insert()`. Correctif : `configure(state="normal")` avant chaque insertion, `configure(state="disabled")` après. Utilisation de `._textbox.insert()` pour préserver les tags de couleur.

**Bug 2** (`core/config_manager.py`) : `set_version(version)` construisait le chemin `minecraft_server_1.21.1/` au lieu de `minecraft_server_PaperMC_1.21.1/`. Correctif : signature étendue `set_version(server_type, version)`.

**Bug 3** (`ui/main_window.py`) : Appel de `config_manager.read_properties()` inexistant (méthode renommée `read_config()` depuis v1.0). Correctif : renommage de l'appel.

**Bug 4** (`core/plugin_manager.py`) : La clé `"downloads"` absente du dictionnaire résultat → compteur toujours à 0. Correctif : ajout de `"downloads": hit.get("downloads", 0)`.

**Bug 5** (`ui/header_bar.py`) : Utilisation de tuples `("Arial", ...)` au lieu de `ctk.CTkFont(...)` → incohérence visuelle cross-platform. Correctif : remplacement par `ctk.CTkFont` partout.

**Dead code** : Suppression de `core/playit_manager.py` (inutilisé depuis v6.0) et retrait de `pyngrok` de `requirements.txt`.

---

## Version 8.3 - Style onglet actif sans fond
**Date :** 04 Mars 2026

**Correctif visuel** (`ui/tab_bar.py`) : L'onglet actif affichait un rectangle `SURFACE (#1e293b)` en fond. Supprimé — `fg_color` toujours `"transparent"`. L'onglet actif est désormais uniquement indiqué par le texte blanc et la barre violette de 2px en bas.

---

## Version 8.2.1 - Fix pack/grid + ScrollableDropdown command
**Date :** 04 Mars 2026
**Bug 1** (`ui/tab_console.py`) : `update_install_state()` utilisait encore `.pack()`/`.pack_forget()` après migration grid de v8.2 → TclError "window isn't packed". Correctif : `grid()`/`grid_remove()` sur col 5 avec `padx=4`.
**Bug 2** (`ui/widgets/scrollable_dropdown.py`) : Première tentative de correctif (guard `is` dans `configure()`). Voir v8.8 pour le correctif définitif.

---

## Version 8.2 - Fix Layout Console + Settings
**Date :** 04 Mars 2026
**Problème 1** (`ui/tab_console.py`) : `grp_server` (CTkFrame pack) s'étirait horizontalement → les boutons Installer/Démarrer disparaissaient hors de la zone visible.
**Correctif** : Réécriture complète de `frame_controls` en grid (col 0→10). Suppression de `grp_server`. Seul col 7 (spacer) prend `weight=1`. `btn_install`/`btn_start` alternent via `.grid()`/`.grid_remove()` sur la même col 5. `entry_bore_ip` masquée via `.grid_remove()`, affichée via `.grid()` dans `set_bore_state()`.
**Problème 2** (`ui/tab_settings.py`) : Badge emoji CTkFrame 22×22 trop petit — `pack_propagate(False)` écrasait l'emoji.
**Correctif** : Badge supprimé. Icône rendue directement par un `CTkLabel` (size=14, text_color=ACCENT) dans le `hdr`.

---

## Version 8.1.1 - Fix update_install_state TclError
**Date :** 04 Mars 2026
**Cause :** `after=self.option_version` dans `update_install_state()` — `option_version` est un enfant de `grp_server`, pas de `frame_controls`. Tkinter exige que le widget passé à `after=` soit un sibling (même parent). → TclError à chaque changement de version, le bouton Installer/Démarrer ne basculait jamais.
**Correctif** (`ui/tab_console.py`) : `grp_server` sauvegardé comme `self.grp_server` dans `__init__`, utilisé comme référence `after=self.grp_server` dans `update_install_state()`.

---

## Version 8.1 - Améliorations Visuelles
**Date :** 04 Mars 2026
**Objectif :** Polissage visuel approfondi de tous les onglets suite à la refonte v8.0.

**`ui/tab_console.py`** (amélioré) :
- Contrôles serveur regroupés dans `grp_server` (CTkFrame BG/BORDER avec séparateur vertical 1px)
- `pill_state` = CTkFrame (RED_TINT/GREEN_TINT) contenant `lbl_state` → statut avec fond coloré
- Ligne header console row=1 "◉ CONSOLE EN DIRECT" (● GREEN + texte MUTED bold)
- `console_box` avec `border_color=BORDER, border_width=1, corner_radius=8`
- Zone de commande avec préfixe "›" ACCENT taille 18
- Renumérotation des rows : controls=0, hdr=1, progress=2, console=3 (weight), input=4

**`ui/tab_players.py`** (amélioré) :
- Avatars colorés par hash du nom du joueur (`AVATAR_PALETTE`, 8 couleurs), avec initiale en blanc
- Badge compteur dynamique `pill_count` (vert = joueurs présents, grisé = serveur vide)
- État vide illustré : titre "Serveur vide" + sous-titre
- Point vert `●` devant le nom de chaque joueur

**`ui/tab_plugins.py`** (amélioré) :
- État initial illustré : titre "Trouver des plugins" + description
- État "aucun résultat" illustré : titre + hint avec le terme recherché
- Bouton "Recherche…" (texte + disabled) pendant la recherche
- Compteur de téléchargements affiché sous la description

**`ui/tab_settings.py`** (amélioré) :
- `_make_section_card(title, icon="")` : badge ACCENT_TINT 22×22 avec icône
- Sections : Paramètres du serveur, Performances du serveur, Planificateur de messages
- Police des labels → `ctk.CTkFont` (cohérence cross-platform)

**`ui/header_bar.py`** (amélioré) :
- Dot coloré `●` dans la pill serveur, couleur selon le type : PaperMC=vert, Vanilla=orange, Fabric=bleu (`TYPE_COLORS` dict)
- `set_server_info` met à jour la couleur du dot
- `update_status` : compte joueurs avec pluriel correct ("1 joueur" / "2 joueurs")

---

## Version 8.0.3 - Fix Badge CTkLabel transparent
**Date :** 04 Mars 2026
**Cause :** `CTkLabel` interdit `text_color="transparent"` → `ValueError`. Le badge joueurs utilisait `transparent` pour se "cacher" visuellement.
**Correctif** (`ui/tab_bar.py`) : Suppression de `text_color`/`fg_color` `"transparent"`. Badge créé avec les vraies couleurs (`fg_color=ACCENT`, `text_color="#ffffff"`). Caché via `.place_forget()` au démarrage (fin de `_place_badge()`). Affiché via `.place()` direct dans `update_badge()` quand `count > 0`, caché via `.place_forget()` quand `count == 0`.

---

## Version 8.0.2 - Hotfix TabBar CTkLabel (Linux)
**Date :** 04 Mars 2026
**Cause racine définitive :** `CTkButton` appelle `canvas._configure()` dans son `__init__` avant mapping fenêtre WM sur Linux → segfault inévitable. `self.update()` insuffisant car le bug est dans le thread de rendu Tk, pas dans l'ordre Python.
**Correctif** (`ui/tab_bar.py`) : Remplacement de tous les `CTkButton` de navigation par des `CTkLabel` + bindings `<Button-1>`/`<Enter>`/`<Leave>`. `CTkLabel` n'utilise pas de canvas → aucun segfault possible. Les IDs d'onglets passent maintenant en minuscules (`"console"`, `"joueurs"`, `"plugins"`, `"parametres"`), `_show_tab()` dans `main_window.py` mis à jour en conséquence.
**Règle projet :** Dans tout widget instancié avant `mainloop()`, préférer `CTkLabel+bindings` à `CTkButton` pour les éléments purement navigationnels.

---

## Version 8.0.1 - Hotfix TabBar Linux
**Date :** 04 Mars 2026
**Cause :** Stack trace : `CTkButton._draw()` → `tkinter._configure()` → segfault dans `ui/tab_bar.py`. Même bug que v7.0.3 : sur Linux, CTkButton tente de se dessiner avant que son frame parent soit mapped. Le `self.update()` de MainWindow ne propage pas aux frames enfants créés après.
**Correctif** (`ui/tab_bar.py`) : Ajout de `self.update()` dans `TabBar.__init__` avant toute instanciation de CTkButton.
Pattern à systématiser : tout widget CTk contenant des CTkButton/CTkSwitch doit appeler `self.update()` en début de `__init__` sur Linux.

---

## Version 8.0 - Refonte UI Dashboard Pro
**Date :** 04 Mars 2026
**Objectif :** Refonte visuelle complète vers le thème "Dashboard Pro" (fond `#0f172a`, accents violet `#6366f1`/`#8b5cf6`, surfaces `#1e293b`).

**Nouveaux fichiers :**
- `ui/header_bar.py` — `HeaderBar(ctk.CTkFrame)` : logo MC, titre MonPanel LOCAL, pill serveur type·version, status pill ●En ligne/●Éteint, CPU + RAM barres de progression (ACCENT/ACCENT2). Méthodes : `update_status(is_running, player_count)`, `update_metrics(cpu, ram)`, `set_server_info(server_type, version)`.
- `ui/tab_bar.py` — `TabBar(ctk.CTkFrame)` : 4 onglets (Console, Joueurs, Plugins, Paramètres) avec indicateur bas 2px ACCENT sur l'onglet actif. Badge numérique ACCENT sur Joueurs. Méthode `update_badge(count)`.

**Architecture (`ui/main_window.py`) :** Suppression de `CTkTabview`. Nouveau layout grid : row 0 HeaderBar, row 1 TabBar, row 2 `frame_content` (weight=1). Les 4 onglets sont placés via `.place(relwidth=1, relheight=1)` et switchés par `.lift()`. `system_monitor` câblé sur `header_bar.update_metrics`. `on_players_update_callback` redirigé vers `_on_players_update` (met à jour tab_players + tab_bar badge + header status). `_action_version_change` appelle `header_bar.set_server_info`.

**Onglets rethémés (aucun changement fonctionnel) :**
- `ui/tab_console.py` : fond BG, barre contrôles SURFACE/BORDER, btn_start ACCENT, btn_stop RED_TINT, btn_bore BLUE_TINT, progress bar fine ACCENT h=4, console BG, lbl_state "● En ligne"/"● Éteint" GREEN/RED.
- `ui/tab_players.py` : header card SURFACE, cartes joueur SURFACE avec avatar ACCENT_TINT 36x36, boutons Kick ORANGE_TINT, Ban RED_TINT.
- `ui/tab_plugins.py` : barre recherche SURFACE, cartes plugin SURFACE avec icône ACCENT_TINT 42x42, progress bar ACCENT h=4.
- `ui/tab_settings.py` : `_make_section_card()` → 3 sections SURFACE (Properties, Performances, Planificateur) avec titres uppercase SUB. Entrées fg=BG, boutons ACCENT.
- `ui/widget_monitor.py` : layout horizontal, SURFACE/BORDER, barres ACCENT/ACCENT2.

**`main.py` :** `ctk.set_default_color_theme("dark-blue")`, callback joueurs → `app._on_players_update`.

---

## Version 7.1 - Widget ScrollableDropdown Custom
**Date :** 04 Mars 2026
**Objectif :** Remplacer CTkComboBox par un widget custom réutilisable offrant un popup avec scroll natif.

**Nouveau fichier** `ui/widgets/scrollable_dropdown.py` :
- `ScrollableDropdown(ctk.CTkButton)` : affiche la valeur courante + `▼`
- Au clic : `CTkToplevel` sans barre de titre (`overrideredirect(True)`, `-topmost`), positionné dynamiquement sous le widget
- Contenu : `CTkScrollableFrame` avec un `CTkButton` par entrée (`anchor="w"`, `fg_color="transparent"`)
- Max 8 entrées visibles (hauteur `n * 30px`), scroll molette au-delà (`<Button-4/5>` Linux)
- Fermeture : `<FocusOut>`, `<Escape>`, ou sélection d'un item
- API compatible : `get()`, `set()`, `configure(values=, state=, command=)` — `state="readonly"` → mappé `"normal"`

**Modifications** `ui/tab_console.py` : import + remplacement de `CTkComboBox` par `ScrollableDropdown`. Toutes les méthodes existantes restent inchangées (API rétrocompatible).

---

## Version 7.0.3 - Hotfix Render Linux
**Date :** 04 Mars 2026
**Cause :** Stack trace confirme : `CTkButton._draw()` → `tkinter._configure()` → segfault. Sur Linux, CustomTkinter tente de dessiner les widgets via canvas avant que la fenêtre soit mapped. Les `CTkButton`/`CTkSwitch` dans `TabSettings` crashent systématiquement.
**Correctif** (`ui/main_window.py`) : Ajout de `self.update()` immédiatement après `super().__init__()` dans `MainWindow`, avant toute instanciation de widget enfant. Force le mapping de la fenêtre Tk avant les rendus CTk.

---

## Version 7.0 - Support Multi-Serveur (PaperMC / Vanilla / Fabric)
**Date :** 04 Mars 2026
**Objectif :** Permettre à l'utilisateur de choisir le type de serveur (PaperMC, Vanilla, Fabric) en plus de la version Minecraft.

**Modifications Apportées :**
- **`core/downloader.py` — Réécriture complète** : `get_versions(server_type)` interroge l'API adaptée selon le type (PaperMC : api.papermc.io, Vanilla : launchermeta.mojang.com avec filtre `type==release`, Fabric : meta.fabricmc.net avec filtre `stable==True`). `download_version(server_type, version, java_exe_path, ...)` dispatche vers trois logiques distinctes. Le dossier cible suit le schéma `minecraft_server_{Type}_{version}/`. Pour Fabric : téléchargement de fabric-installer.jar (0→50%), lancement Java avec `-mcversion`/`-loader`/`-downloadMinecraft` (50→100%), nettoyage de l'installateur.
- **`core/server_manager.py`** : Ajout de `self.server_type = "PaperMC"` et `self.launch_jar = "server.jar"` dans `__init__`. `set_version(server_type, version)` (signature étendue) calcule `server_dir = minecraft_server_{type}_{version}/` et positionne `launch_jar` à `fabric-server-launch.jar` pour Fabric ou `server.jar` sinon. Le `subprocess.Popen` utilise désormais `self.launch_jar` au lieu du hardcode `"server.jar"`.
- **`ui/tab_console.py`** : Ajout du `CTkOptionMenu` Type (`PaperMC`/`Vanilla`/`Fabric`, largeur 110) placé avant le menu Version. Nouveau paramètre `on_type_change` dans la signature. Méthodes `_on_type_selected` et `set_loading_state(loading)` ajoutées.
- **`ui/main_window.py`** : `_initialize_app()` initialise `current_server_type = "PaperMC"` et appelle `get_versions("PaperMC")`. `_on_versions_fetched()` appelle `set_loading_state(False)` avant d'afficher. Nouvelle méthode `_action_type_change(server_type)`. `_action_download()` délègue à un thread `prepare_and_download` qui, pour Fabric uniquement, appelle `ensure_java()` + `get_java_executable()`.

---

## Version 6.3 - Scroll Molette Universel
**Date :** 04 Mars 2026
**Objectif :** Rendre le scroll à la molette fonctionnel sur tous les onglets contenant une zone défilante, sur Linux (et Windows/macOS).

**Modifications Apportées :**
- **Refactorisation du scroll dans `ui/tab_settings.py`** : Remplacement du hack `tk.Canvas` + `CTkFrame(canvas)` (incompatible Linux) par un `CTkScrollableFrame` natif. Suppression de `import tkinter as tk`, de `self._canvas`, `self._scrollbar`.
- **Propagation molette** : Pattern `_bind_mousewheel(widget)` (récursif) + `_on_mousewheel(event)` appliqué sur `tab_settings`, `tab_players` et `tab_plugins`. Re-binding à la fin de chaque méthode de rendu dynamique.
- **Note technique** : Les bindings `<Button-4>`/`<Button-5>` (Linux) et `<MouseWheel>` (Windows/macOS) sont appliqués récursivement car Tkinter ne propage pas ces événements vers les widgets parents.

---

## Version 6.2 - Améliorations de Confort
**Date :** 04 Mars 2026
**Objectif :** Améliorer l'ergonomie de l'interface sans créer de nouveaux fichiers.

**Modifications Apportées :**
- **Historique des commandes** (`ui/tab_console.py`) : Mémorisation des 50 dernières commandes. Navigation avec flèches ↑/↓.
- **Console colorée** (`ui/tab_console.py`) : Colorisation via tags du widget `Text` interne. Rouge (erreurs), jaune (warnings), bleu clair (système), gris clair (standard).
- **Planificateur Auto-Broadcast** (`core/server_manager.py` + `ui/tab_settings.py` + `ui/main_window.py`) : `start_scheduler(message, interval_minutes)` — thread daemon envoyant `say {message}` périodiquement. Section UI dédiée dans Paramètres : champ message, menu intervalle, switch d'activation.

---

## Version 6.1 - Éditeur de Performances
**Date :** 04 Mars 2026
**Objectif :** Contrôle de la RAM allouée et activation des Aikar Flags depuis l'interface.

**Modifications Apportées :**
- **Persistance** (`core/config_manager.py`) : `load_performance_config()` / `save_performance_config(ram_mb, aikar_flags)` dans `panel_config.json`.
- **Démarrage dynamique** (`core/server_manager.py`) : `start_server(aikar_flags=False)`. En mode Aikar, 15 flags JVM G1GC optimisés remplacent les simples `-Xms`/`-Xmx`.
- **Section UI** (`ui/tab_settings.py`) : `CTkOptionMenu` RAM (512/1024/2048/4096/6144/8192 Mo), `CTkSwitch` Aikar Flags, bouton sauvegarde.

---

## Version 6.0 - Tunneling avec Bore
**Date :** 04 Mars 2026
**Objectif :** Rendre le serveur accessible depuis Internet sans configuration de routeur.

**Modifications Apportées :**
- **`core/bore_manager.py`** : Téléchargement automatique de Bore depuis GitHub (multiplateforme Windows/Mac/Linux x86/arm). Lancement asynchrone, interception du port distant par regex.
- **UI** (`ui/tab_console.py`) : Bouton "Public" avec affichage de l'IP publique en lecture seule.

---

## Version 5.1 - Tunneling avec Playit.gg
**Date :** 02 Mars 2026
*(Remplacé par Bore en v6.0 — `core/playit_manager.py` supprimé en v8.4)*

---

## Version 5.0 - Gestionnaire de Plugins Modrinth
**Date :** 02 Mars 2026
**Objectif :** Recherche, téléchargement et installation de plugins depuis l'API Modrinth.

**Modifications Apportées :**
- **`core/plugin_manager.py`** : `PluginManager` — `/v2/search` pour la recherche, `/v2/project/...` pour l'URL du `.jar`. Téléchargement dans `plugins/` du serveur courant.
- **`ui/tab_plugins.py`** : Barre de recherche + cartes résultats dans `CTkScrollableFrame` + barre de progression.
- **Architecture thread-safe** : Requêtes HTTP non-bloquantes via `threading.Thread(daemon=True)`, communication UI via `after(0)`.

---

## Version 4.0 - Gestion des Joueurs en Temps Réel
**Date :** 02 Mars 2026
**Modifications Apportées :**
- **Parsing logs** (`server_manager.py`) : Interception `joined/left the game` par regex. Nettoyage codes ANSI.
- **`ui/tab_players.py`** : Liste joueurs avec boutons Op/Kick/Ban connectés au stdin Java. Bouton rafraîchissement (commande `list`).
- **Thread-safe** (`main.py`) : Mise à jour via `.after(0)`.

---

## Version 3.0 - Runtimes Java Dynamiques
**Date :** 02 Mars 2026
**Modifications Apportées :**
- **`java_manager.py`** : API Adoptium V3 pour télécharger les JREs selon OS et architecture. Extraction dans `/runtimes/java_X/`.
- **Détection automatique** (`server_manager.py`) : Java 8 (≤1.16), Java 16 (1.17), Java 17 (≤1.20.4), Java 21 (≥1.20.5).

---

## Version 2.0 - Gestion Dynamique des Versions
**Date :** 02 Mars 2026
**Modifications Apportées :**
- **API PaperMC** (`downloader.py`) : Récupération asynchrone de toutes les versions.
- **Menu déroulant** (`tab_console.py`) : `CTkOptionMenu` pour choisir la version.
- **Dossiers isolés** (`server_manager.py`) : `minecraft_server_{TYPE}_{VERSION}/`.
- **Bouton Installer/Démarrer** (`main_window.py`) : Bascule selon présence locale du serveur.

---

## Version 1.0 - Refactorisation Architecture MVC
**Date :** 02 Mars 2026
**Objectif :** Transformer `app.py` en architecture modulaire Core/UI.

- `main.py` : Point d'entrée, injection de dépendances
- `core/server_manager.py`, `core/downloader.py`, `core/config_manager.py`, `core/system_monitor.py`
- `ui/main_window.py`, `ui/tab_console.py`, `ui/tab_settings.py`, `ui/widget_monitor.py`

---

## Initialisation - Proof Of Concept
**Objectif Initial :** Interface `CustomTkinter` sombre, lancement Java non-bloquant via `threading`, génération auto de `eula.txt`.
