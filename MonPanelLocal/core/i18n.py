# EasyHost MC — core/i18n.py
# Système de traduction FR / EN
# Usage : from core.i18n import t, set_lang, get_lang

from __future__ import annotations

# ---------------------------------------------------------------------------
# Dictionnaire Français (référence)
# ---------------------------------------------------------------------------
FR: dict[str, str] = {

    # ── tab_console.py ──────────────────────────────────────────────────────
    "console.type":                    "Type de serveur",
    "console.version":                 "Version",
    "console.install":                 "Installer",
    "console.start":                   "Démarrer",
    "console.stop":                    "Arrêter",
    "console.public":                  "Rendre public",
    "console.tunnel_active":           "Tunnel actif",
    "console.offline":                 "Hors ligne",
    "console.online":                  "En ligne",
    "console.send":                    "Envoyer",
    "console.cmd_hint":                "Entrez une commande…",
    "console.live_header":             "Console en direct",
    "console.loading":                 "Chargement…",
    "console.api_error":               "Erreur API : impossible de récupérer les versions.",
    "console.system_fetching":         "Récupération des versions disponibles…",
    "console.system_versions_available": "Versions disponibles récupérées.",
    "console.system_start":            "Démarrage du serveur…",
    "console.system_already_running":  "Le serveur est déjà en cours d'exécution.",
    "console.system_jar_missing":      "Fichier JAR introuvable. Veuillez d'abord installer le serveur.",
    "console.system_eula_created":     "EULA acceptée et créée.",
    "console.system_stopping":         "Arrêt du serveur en cours…",
    "console.system_stopped":          "Serveur arrêté.",
    "console.system_server_off":       "Le serveur n'est pas en cours d'exécution.",
    "console.system_bore_stopped":     "Tunnel Bore arrêté.",
    "console.system_bore_starting":    "Démarrage du tunnel Bore…",
    "console.system_bore_ip":          "IP publique du tunnel",
    "console.error_bore_failed":       "Échec du démarrage du tunnel Bore.",
    "console.error_command":           "Erreur lors de l'exécution de la commande.",

    # ── tab_players.py ───────────────────────────────────────────────────────
    "players.title":                   "Joueurs connectés",
    "players.subtitle":                "Liste des joueurs actuellement en ligne",
    "players.empty_title":             "Aucun joueur connecté",
    "players.empty_sub":               "Le serveur est vide pour l'instant.",
    "players.refresh":                 "Rafraîchir",
    "players.online":                  "En ligne",
    "players.count_one":               "1 joueur",
    "players.count_many":              "{n} joueurs",

    # ── tab_plugins.py ───────────────────────────────────────────────────────
    "plugins.search_placeholder":      "Rechercher un plugin…",
    "plugins.search_btn":              "Rechercher",
    "plugins.searching":               "Recherche en cours…",
    "plugins.prompt_title":            "Recherchez un plugin",
    "plugins.prompt_sub":              "Entrez un nom dans la barre de recherche ci-dessus.",
    "plugins.no_results_title":        "Aucun résultat",
    "plugins.no_results_hint":         "Essayez un autre terme de recherche.",
    "plugins.install":                 "Installer",

    # ── tab_settings.py ──────────────────────────────────────────────────────
    "settings.section_server":         "Paramètres du serveur",
    "settings.section_perf":           "Performances",
    "settings.section_scheduler":      "Planificateur de messages",
    "settings.section_lang":           "Langue",
    "settings.port":                   "Port",
    "settings.max_players":            "Joueurs maximum",
    "settings.motd":                   "Message du jour (MOTD)",
    "settings.difficulty":             "Difficulté",
    "settings.gamemode":               "Mode de jeu",
    "settings.save":                   "Enregistrer",
    "settings.saved_ok":               "Paramètres enregistrés avec succès.",
    "settings.save_error":             "Erreur lors de l'enregistrement des paramètres.",
    "settings.ram":                    "RAM allouée (Mo)",
    "settings.aikar":                  "Flags Aikar",
    "settings.aikar_desc":             "Active les flags JVM recommandés pour les serveurs Minecraft.",
    "settings.save_perf":              "Enregistrer les performances",
    "settings.perf_saved_ok":          "Paramètres de performance enregistrés.",
    "settings.perf_save_error":        "Erreur lors de l'enregistrement des performances.",
    "settings.scheduler_msg":          "Message planifié",
    "settings.scheduler_msg_placeholder": "Entrez le message à diffuser…",
    "settings.scheduler_interval":     "Intervalle (secondes)",
    "settings.scheduler_enable":       "Activer le planificateur",
    "settings.lang_label":             "Langue de l'interface",

    # ── tab_bar.py ───────────────────────────────────────────────────────────
    "tabs.console":                    "Console",
    "tabs.players":                    "Joueurs",
    "tabs.plugins":                    "Plugins",
    "tabs.settings":                   "Paramètres",

    # ── header_bar.py ────────────────────────────────────────────────────────
    "header.title":                    "EasyHost MC",
    "header.subtitle":                 "Panneau de gestion de serveur Minecraft",
    "header.offline":                  "Hors ligne",
    "header.online":                   "En ligne",

    # ── main_window.py / main.py ─────────────────────────────────────────────
    "app.title":                       "EasyHost MC",
    "app.closing_title":               "Fermeture",
    "app.closing_log":                 "Fermeture de l'application…",
    "app.install_done":                "Installation terminée avec succès.",
    "app.plugin_installed":            "Plugin installé avec succès.",
    "app.plugin_error":                "Erreur lors de l'installation du plugin.",
    "app.search_error":                "Erreur lors de la recherche de plugins.",
    "app.bore_error":                  "Impossible de démarrer le tunnel Bore.",
    "app.no_version_selected":         "Veuillez sélectionner une version avant de continuer.",
}

# ---------------------------------------------------------------------------
# Dictionnaire Anglais
# ---------------------------------------------------------------------------
EN: dict[str, str] = {

    # ── tab_console.py ──────────────────────────────────────────────────────
    "console.type":                    "Server type",
    "console.version":                 "Version",
    "console.install":                 "Install",
    "console.start":                   "Start",
    "console.stop":                    "Stop",
    "console.public":                  "Make public",
    "console.tunnel_active":           "Tunnel active",
    "console.offline":                 "Offline",
    "console.online":                  "Online",
    "console.send":                    "Send",
    "console.cmd_hint":                "Enter a command…",
    "console.live_header":             "Live console",
    "console.loading":                 "Loading…",
    "console.api_error":               "API error: unable to fetch versions.",
    "console.system_fetching":         "Fetching available versions…",
    "console.system_versions_available": "Available versions retrieved.",
    "console.system_start":            "Starting server…",
    "console.system_already_running":  "The server is already running.",
    "console.system_jar_missing":      "JAR file not found. Please install the server first.",
    "console.system_eula_created":     "EULA accepted and created.",
    "console.system_stopping":         "Stopping server…",
    "console.system_stopped":          "Server stopped.",
    "console.system_server_off":       "The server is not running.",
    "console.system_bore_stopped":     "Bore tunnel stopped.",
    "console.system_bore_starting":    "Starting Bore tunnel…",
    "console.system_bore_ip":          "Tunnel public IP",
    "console.error_bore_failed":       "Failed to start Bore tunnel.",
    "console.error_command":           "Error executing command.",

    # ── tab_players.py ───────────────────────────────────────────────────────
    "players.title":                   "Connected players",
    "players.subtitle":                "Players currently online",
    "players.empty_title":             "No players online",
    "players.empty_sub":               "The server is empty for now.",
    "players.refresh":                 "Refresh",
    "players.online":                  "Online",
    "players.count_one":               "1 player",
    "players.count_many":              "{n} players",

    # ── tab_plugins.py ───────────────────────────────────────────────────────
    "plugins.search_placeholder":      "Search for a plugin…",
    "plugins.search_btn":              "Search",
    "plugins.searching":               "Searching…",
    "plugins.prompt_title":            "Search for a plugin",
    "plugins.prompt_sub":              "Enter a name in the search bar above.",
    "plugins.no_results_title":        "No results",
    "plugins.no_results_hint":         "Try a different search term.",
    "plugins.install":                 "Install",

    # ── tab_settings.py ──────────────────────────────────────────────────────
    "settings.section_server":         "Server settings",
    "settings.section_perf":           "Performance",
    "settings.section_scheduler":      "Message scheduler",
    "settings.section_lang":           "Language",
    "settings.port":                   "Port",
    "settings.max_players":            "Max players",
    "settings.motd":                   "Message of the day (MOTD)",
    "settings.difficulty":             "Difficulty",
    "settings.gamemode":               "Game mode",
    "settings.save":                   "Save",
    "settings.saved_ok":               "Settings saved successfully.",
    "settings.save_error":             "Error saving settings.",
    "settings.ram":                    "Allocated RAM (MB)",
    "settings.aikar":                  "Aikar flags",
    "settings.aikar_desc":             "Enable recommended JVM flags for Minecraft servers.",
    "settings.save_perf":              "Save performance settings",
    "settings.perf_saved_ok":          "Performance settings saved.",
    "settings.perf_save_error":        "Error saving performance settings.",
    "settings.scheduler_msg":          "Scheduled message",
    "settings.scheduler_msg_placeholder": "Enter the message to broadcast…",
    "settings.scheduler_interval":     "Interval (seconds)",
    "settings.scheduler_enable":       "Enable scheduler",
    "settings.lang_label":             "Interface language",

    # ── tab_bar.py ───────────────────────────────────────────────────────────
    "tabs.console":                    "Console",
    "tabs.players":                    "Players",
    "tabs.plugins":                    "Plugins",
    "tabs.settings":                   "Settings",

    # ── header_bar.py ────────────────────────────────────────────────────────
    "header.title":                    "EasyHost MC",
    "header.subtitle":                 "Minecraft server management panel",
    "header.offline":                  "Offline",
    "header.online":                   "Online",

    # ── main_window.py / main.py ─────────────────────────────────────────────
    "app.title":                       "EasyHost MC",
    "app.closing_title":               "Closing",
    "app.closing_log":                 "Closing application…",
    "app.install_done":                "Installation completed successfully.",
    "app.plugin_installed":            "Plugin installed successfully.",
    "app.plugin_error":                "Error installing plugin.",
    "app.search_error":                "Error searching for plugins.",
    "app.bore_error":                  "Unable to start Bore tunnel.",
    "app.no_version_selected":         "Please select a version before continuing.",
}

# ---------------------------------------------------------------------------
# Catalogue complet (ajout de nouvelles langues possible ici)
# ---------------------------------------------------------------------------
_CATALOGUE: dict[str, dict[str, str]] = {
    "fr": FR,
    "en": EN,
}

# ---------------------------------------------------------------------------
# État global de la langue
# ---------------------------------------------------------------------------
_LANG: str = "fr"


def set_lang(lang: str) -> None:
    """Change la langue active. Accepte 'fr' ou 'en' (insensible à la casse)."""
    global _LANG
    key = lang.lower()
    if key not in _CATALOGUE:
        raise ValueError(
            f"Langue '{lang}' non supportée. Langues disponibles : {list(_CATALOGUE)}"
        )
    _LANG = key


def get_lang() -> str:
    """Retourne la langue active ('fr' ou 'en')."""
    return _LANG


def t(key: str) -> str:
    """
    Retourne la traduction de *key* dans la langue active.
    Si la clé est absente du dictionnaire actif, retourne la clé elle-même
    (comportement sûr : jamais de KeyError à l'exécution).
    """
    return _CATALOGUE.get(_LANG, FR).get(key, key)
