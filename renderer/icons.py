# renderer/icons.py
# Base de Datos de Iconos Material para PyPhonOS
# 200+ iconos Unicode organizados por categoría con búsqueda y colorización.

from renderer.colors import Color, Palette


class IconDB:
    """
    Base de datos centralizada de iconos Material Design.
    Usa caracteres Unicode como fallback visual para cada icono.

    Uso:
        icon = IconDB.get("home")           # → "⌂"
        icon = IconDB.get("settings")       # → "⚙"
        icons = IconDB.search("arrow")      # → {"arrow_up": "↑", ...}
        cats = IconDB.categories()          # → ["navigation", "action", ...]
        all_nav = IconDB.by_category("navigation")
    """

    # ─────────────────────────────────────────
    # CATÁLOGO COMPLETO DE ICONOS
    # ─────────────────────────────────────────

    ICONS = {
        # ── Navegación ──
        "home":                 "⌂",
        "menu":                 "≡",
        "menu_open":            "☰",
        "back":                 "←",
        "forward":              "→",
        "arrow_up":             "↑",
        "arrow_down":           "↓",
        "arrow_left":           "←",
        "arrow_right":          "→",
        "chevron_left":         "‹",
        "chevron_right":        "›",
        "chevron_up":           "ˆ",
        "chevron_down":         "ˇ",
        "expand_more":          "▼",
        "expand_less":          "▲",
        "close":                "✕",
        "fullscreen":           "⛶",
        "navigate_before":      "◂",
        "navigate_next":        "▸",
        "first_page":           "⏮",
        "last_page":            "⏭",
        "subdirectory":         "↳",
        "launch":               "↗",
        "more_vert":            "⋮",
        "more_horiz":           "⋯",
        "apps":                 "⊞",
        "dashboard":            "▦",
        "swap_horiz":           "⇔",
        "swap_vert":            "⇕",
        "unfold_more":          "⥮",
        "unfold_less":          "⥯",

        # ── Acciones ──
        "search":               "⌕",
        "add":                  "+",
        "remove":               "−",
        "edit":                 "✎",
        "delete":               "🗑",
        "save":                 "💾",
        "done":                 "✓",
        "check":                "✓",
        "check_circle":         "✔",
        "cancel":               "✗",
        "clear":                "✕",
        "refresh":              "↺",
        "undo":                 "↶",
        "redo":                 "↷",
        "copy":                 "⎘",
        "cut":                  "✂",
        "paste":                "📋",
        "share":                "↗",
        "download":             "⬇",
        "upload":               "⬆",
        "print":                "🖨",
        "send":                 "➤",
        "reply":                "↩",
        "reply_all":            "↩↩",
        "forward_msg":          "↪",
        "attach":               "📎",
        "link":                 "🔗",
        "unlink":               "⛓",
        "pin":                  "📌",
        "flag":                 "🚩",
        "archive":              "📦",
        "filter":               "⧩",
        "sort":                 "⇅",
        "drag_handle":          "⠿",
        "zoom_in":              "🔍+",
        "zoom_out":             "🔍-",
        "select_all":           "☑",
        "deselect_all":         "☐",
        "power":                "⏻",
        "settings":             "⚙",
        "tune":                 "⚙",
        "build":                "🔧",
        "code":                 "</>",
        "bug":                  "🐛",
        "extension":            "🧩",
        "translate":            "🌐",
        "language":             "🌐",

        # ── Estado / Favoritos ──
        "favorite":             "♡",
        "favorite_fill":        "♥",
        "star":                 "☆",
        "star_fill":            "★",
        "star_half":            "⯪",
        "bookmark":             "🔖",
        "bookmark_border":      "☆",
        "thumb_up":             "👍",
        "thumb_down":           "👎",
        "visibility":           "👁",
        "visibility_off":       "🚫",
        "lock":                 "🔒",
        "lock_open":            "🔓",
        "key":                  "🔑",
        "shield":               "🛡",
        "verified":             "✓",
        "new_releases":         "✦",
        "label":                "🏷",
        "info":                 "ℹ",
        "help":                 "?",
        "warning":              "⚠",
        "error":                "✗",
        "report":               "⚑",

        # ── Comunicación ──
        "chat":                 "💬",
        "chat_bubble":          "💬",
        "message":              "✉",
        "email":                "📧",
        "mail":                 "✉",
        "inbox":                "📥",
        "outbox":               "📤",
        "drafts":               "📝",
        "phone":                "📞",
        "call":                 "☎",
        "call_end":             "📵",
        "video_call":           "📹",
        "contact":              "👤",
        "contacts":             "👥",
        "group":                "👥",
        "person_add":           "👤+",
        "person_remove":        "👤-",
        "notification":         "🔔",
        "notification_off":     "🔕",
        "campaign":             "📢",

        # ── Media ──
        "play":                 "▶",
        "pause":                "⏸",
        "stop":                 "⏹",
        "record":               "⏺",
        "skip_next":            "⏭",
        "skip_prev":            "⏮",
        "fast_forward":         "⏩",
        "fast_rewind":          "⏪",
        "repeat":               "🔁",
        "shuffle":              "🔀",
        "volume_up":            "🔊",
        "volume_down":          "🔉",
        "volume_mute":          "🔇",
        "volume_off":           "🔇",
        "mic":                  "🎤",
        "mic_off":              "🎤✕",
        "camera":               "📷",
        "photo":                "🖼",
        "movie":                "🎬",
        "music":                "🎵",
        "headset":              "🎧",
        "equalizer":            "🎛",
        "playlist":             "🎶",
        "album":                "💿",
        "radio":                "📻",
        "tv":                   "📺",
        "cast":                 "📡",
        "screen_share":         "🖥",
        "brightness":           "☀",
        "brightness_low":       "🌙",
        "flash_on":             "⚡",
        "flash_off":            "⚡✕",

        # ── Dispositivo / Sistema ──
        "wifi":                 "📶",
        "wifi_off":             "📶✕",
        "bluetooth":            "ᛒ",
        "bluetooth_off":        "ᛒ✕",
        "battery_full":         "🔋",
        "battery_low":          "🪫",
        "battery_charging":     "⚡🔋",
        "signal":               "📶",
        "airplane":             "✈",
        "gps":                  "📍",
        "location":             "📍",
        "compass":              "🧭",
        "storage":              "💾",
        "sd_card":              "💳",
        "usb":                  "🔌",
        "nfc":                  "📱",
        "fingerprint":          "👆",
        "face":                 "😊",
        "qr_code":              "⊞",
        "barcode":              "⊞",
        "developer_mode":       "💻",
        "memory":               "🧠",
        "speed":                "⚡",
        "timer":                "⏲",
        "alarm":                "⏰",
        "schedule":             "📅",
        "calendar":             "📅",
        "clock":                "🕐",
        "hourglass":            "⏳",
        "update":               "🔄",
        "sync":                 "🔄",
        "cloud":                "☁",
        "cloud_download":       "☁↓",
        "cloud_upload":         "☁↑",
        "cloud_off":            "☁✕",

        # ── Archivos / Documentos ──
        "folder":               "📁",
        "folder_open":          "📂",
        "file":                 "📄",
        "file_copy":            "📄📄",
        "description":          "📝",
        "article":              "📰",
        "note":                 "🗒",
        "list":                 "☰",
        "grid_view":            "⊞",
        "table":                "▦",
        "chart":                "📊",
        "pie_chart":            "◔",
        "bar_chart":            "📊",
        "analytics":            "📈",
        "trending_up":          "📈",
        "trending_down":        "📉",

        # ── Mapas / Lugares ──
        "map":                  "🗺",
        "place":                "📍",
        "navigation_map":       "🧭",
        "directions":           "➤",
        "near_me":              "📍",
        "store":                "🏪",
        "restaurant":           "🍽",
        "hotel":                "🏨",
        "hospital":             "🏥",
        "school":               "🏫",
        "local_parking":        "🅿",
        "gas_station":          "⛽",
        "flight":               "✈",
        "train":                "🚂",
        "bus":                  "🚌",
        "car":                  "🚗",

        # ── Social ──
        "public":               "🌐",
        "people":               "👥",
        "cake":                 "🎂",
        "celebration":          "🎉",
        "mood":                 "😊",
        "mood_bad":             "😞",
        "emoji":                "😀",
        "thumb":                "👍",
        "heart":                "❤",
        "workspace":            "🏢",
    }

    # ─── Categorías ───
    CATEGORIES = {
        "navigation":    ["home", "menu", "menu_open", "back", "forward", "arrow_up", "arrow_down",
                          "arrow_left", "arrow_right", "chevron_left", "chevron_right",
                          "close", "more_vert", "more_horiz", "apps", "dashboard"],
        "action":        ["search", "add", "remove", "edit", "delete", "save", "done", "check",
                          "cancel", "refresh", "undo", "redo", "copy", "cut", "paste",
                          "share", "download", "upload", "send", "attach", "link",
                          "settings", "build", "code", "translate"],
        "status":        ["favorite", "favorite_fill", "star", "star_fill", "bookmark",
                          "thumb_up", "thumb_down", "visibility", "visibility_off",
                          "lock", "lock_open", "info", "warning", "error"],
        "communication": ["chat", "email", "mail", "phone", "call", "video_call",
                          "contact", "contacts", "notification", "notification_off"],
        "media":         ["play", "pause", "stop", "skip_next", "skip_prev", "volume_up",
                          "volume_mute", "mic", "camera", "photo", "music", "movie"],
        "device":        ["wifi", "bluetooth", "battery_full", "signal", "gps", "location",
                          "storage", "fingerprint", "memory", "speed", "timer", "alarm",
                          "clock", "cloud", "sync", "update"],
        "files":         ["folder", "folder_open", "file", "description", "article",
                          "list", "grid_view", "table", "chart"],
        "maps":          ["map", "place", "directions", "near_me", "store",
                          "flight", "train", "car"],
        "social":        ["public", "people", "emoji", "heart", "celebration", "cake"],
    }

    @classmethod
    def get(cls, name, default="?"):
        """Obtiene el carácter Unicode de un icono por nombre."""
        return cls.ICONS.get(name, default)

    @classmethod
    def search(cls, query):
        """Busca iconos cuyo nombre contenga la cadena de búsqueda."""
        query = query.lower()
        return {
            name: char for name, char in cls.ICONS.items()
            if query in name.lower()
        }

    @classmethod
    def categories(cls):
        """Retorna la lista de categorías disponibles."""
        return list(cls.CATEGORIES.keys())

    @classmethod
    def by_category(cls, category):
        """Retorna todos los iconos de una categoría."""
        names = cls.CATEGORIES.get(category, [])
        return {name: cls.ICONS.get(name, "?") for name in names}

    @classmethod
    def all_icons(cls):
        """Retorna todos los iconos disponibles."""
        return dict(cls.ICONS)

    @classmethod
    def count(cls):
        """Retorna el número total de iconos disponibles."""
        return len(cls.ICONS)

    @classmethod
    def exists(cls, name):
        """Verifica si un icono existe en la base de datos."""
        return name in cls.ICONS
