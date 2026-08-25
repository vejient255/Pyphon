#!/usr/bin/env python3
"""Test rápido de todos los módulos nuevos de PyPhonOS."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test 1: Colores y Palette
from renderer.colors import Color, Palette
print("[OK] renderer.colors")

# Test 2: Icons
from renderer.icons import IconDB
print(f"[OK] renderer.icons — {IconDB.count()} iconos cargados")
print(f"     Categorías: {IconDB.categories()}")

# Test 3: Effects  
from renderer.effects import ContrastEngine, DynamicShadow, GlassPanel
bg = Color(103, 80, 164)
tc = ContrastEngine.get_text_color(bg)
print(f"[OK] renderer.effects — Contraste para purple: rgb({tc.r},{tc.g},{tc.b})")

# Test 4: Animation
from core.animation import AnimationManager, Easing, Tween
print(f"[OK] core.animation — Easings: {list(Easing.FUNCTIONS.keys())}")

# Test 5: Navigator
from core.navigator import Screen, Navigator, Transition
nav = Navigator(360)
print(f"[OK] core.navigator — Stack depth: {nav.stack_depth}")

# Test 6: Inspector
from core.inspector import WidgetInspector
inspector = WidgetInspector()
print(f"[OK] core.inspector — Enabled: {inspector.enabled}")

# Test 7: Declarative
from core.declarative import build_ui, find_widget_by_id
print("[OK] core.declarative")

# Test 8: Form Validator
from core.form_validator import FormValidator, ValidationRule
rule = ValidationRule("email")
assert rule.validate("test@mail.com") == True
assert rule.validate("not-email") == False
print("[OK] core.form_validator — Email validation works")

# Test 9: i18n
from core.i18n import I18nManager, t
i18n = I18nManager("es")
i18n.add_translations("es", {"app": {"title": "PyPhonOS"}})
i18n.add_translations("en", {"app": {"title": "PyPhonOS"}})
assert t("app.title") == "PyPhonOS"
print(f"[OK] core.i18n — Languages: {i18n.available_languages}")

# Test 10: Theme
from core.theme import ThemeManager
print("[OK] core.theme")

print("\n========================================")
print("   ✅ TODOS LOS MÓDULOS FUNCIONAN ✅")
print("========================================")
