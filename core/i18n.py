# core/i18n.py
# Sistema de Internacionalización (i18n) para PyPhonOS
# Cambia todos los textos de la app al idioma activo con una sola línea.

import json
import os


class I18nManager:
    """
    Gestor de traducciones multilingüe.
    Soporta diccionarios anidados con acceso por puntos.

    Uso:
        i18n = I18nManager(default_lang="es")

        # Registrar traducciones
        i18n.add_translations("es", {
            "settings": {
                "title": "Configuración",
                "subtitle": "Gestiona tus preferencias",
                "identity": "IDENTIDAD",
                "username": "Nombre de usuario",
                "email": "Correo electrónico",
            },
            "actions": {
                "save": "Guardar",
                "cancel": "Cancelar",
                "apply": "Aplicar cambios",
            },
            "nav": {
                "home": "Inicio",
                "apps": "Aplicaciones",
                "settings": "Ajustes",
            }
        })

        i18n.add_translations("en", {
            "settings": {
                "title": "Settings",
                "subtitle": "Manage your preferences",
                ...
            }
        })

        # Usar traducciones
        label.text = i18n.t("settings.title")      # → "Configuración"
        i18n.set_language("en")
        label.text = i18n.t("settings.title")      # → "Settings"
    """

    INSTANCE = None

    def __init__(self, default_lang="es"):
        self._current_lang = default_lang
        self._translations = {}   # {lang: {key: value}}
        self._listeners = []      # Callbacks para re-render al cambiar idioma
        self._fallback_lang = "en"
        I18nManager.INSTANCE = self

    @property
    def current_language(self):
        return self._current_lang

    @property
    def available_languages(self):
        return list(self._translations.keys())

    def add_translations(self, lang, translations: dict):
        """Registra un diccionario de traducciones para un idioma."""
        if lang not in self._translations:
            self._translations[lang] = {}
        self._merge_deep(self._translations[lang], translations)

    def load_from_json(self, lang, json_path):
        """Carga traducciones desde un archivo JSON."""
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.add_translations(lang, data)

    def load_directory(self, directory):
        """
        Carga todos los archivos JSON de un directorio.
        El nombre del archivo = código de idioma.
        Ej: locales/es.json, locales/en.json
        """
        if not os.path.isdir(directory):
            print(f"[i18n] Directorio no encontrado: {directory}")
            return
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                lang = filename[:-5]  # quitar .json
                self.load_from_json(lang, os.path.join(directory, filename))

    def t(self, key, **kwargs):
        """
        Traduce una clave usando notación de puntos.

        Args:
            key: Clave de traducción (ej: "settings.title")
            **kwargs: Parámetros de interpolación (ej: name="Juan")

        Returns:
            Texto traducido o la clave si no se encuentra.

        Ejemplo:
            i18n.t("greeting", name="Juan")
            # Con traducción: "greeting": "Hola {name}"
            # Resultado: "Hola Juan"
        """
        # Buscar en idioma actual
        value = self._resolve_key(self._current_lang, key)

        # Fallback al idioma secundario
        if value is None and self._current_lang != self._fallback_lang:
            value = self._resolve_key(self._fallback_lang, key)

        # Si no se encontró, retornar la clave
        if value is None:
            return f"[{key}]"

        # Interpolación de variables
        if kwargs:
            try:
                value = value.format(**kwargs)
            except (KeyError, IndexError):
                pass

        return value

    def set_language(self, lang):
        """Cambia el idioma activo y notifica a los listeners."""
        if lang == self._current_lang:
            return
        if lang not in self._translations:
            print(f"[i18n] Idioma '{lang}' no encontrado. Disponibles: {self.available_languages}")
            return
        self._current_lang = lang
        self._notify()

    def add_listener(self, callback):
        """Registra un callback que será llamado al cambiar de idioma."""
        self._listeners.append(callback)

    def remove_listener(self, callback):
        self._listeners = [l for l in self._listeners if l is not callback]

    def _resolve_key(self, lang, dotted_key):
        """Resuelve una clave con puntos en el diccionario anidado."""
        if lang not in self._translations:
            return None
        data = self._translations[lang]
        parts = dotted_key.split('.')
        for part in parts:
            if isinstance(data, dict) and part in data:
                data = data[part]
            else:
                return None
        return data if isinstance(data, str) else None

    def _merge_deep(self, base, overlay):
        """Merge recursivo de diccionarios."""
        for key, value in overlay.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_deep(base[key], value)
            else:
                base[key] = value

    def _notify(self):
        """Notifica a todos los listeners del cambio de idioma."""
        for listener in self._listeners:
            try:
                listener()
            except Exception as e:
                print(f"[i18n] Error en listener: {e}")


# Atajo global
def t(key, **kwargs):
    """Función global de traducción. Usa la instancia singleton de I18nManager."""
    if I18nManager.INSTANCE:
        return I18nManager.INSTANCE.t(key, **kwargs)
    return f"[{key}]"
