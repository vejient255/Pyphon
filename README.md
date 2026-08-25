# PyPhonOS - Framework UI para Python

Un framework de interfaz de usuario para Python con renderizado SDL2 y estilo neumórfico.

## 🎨 Características

- **Renderizado SDL2**: Utiliza PySDL2 para renderizado gráfico nativo de alto rendimiento
- **Diseño Neumórfico**: Widgets con estilo neumórfico moderno (sombras suaves, elevaciones)
- **Arquitectura Modular**: Organización en módulos (core, widgets, renderer, events)
- **Sistema de Navegación**: Gestión de pantallas y navegación entre vistas
- **Animaciones**: Sistema de animaciones integrado
- **Temas**: Soporte para temas personalizables
- **Validación de Formularios**: Sistema de validación declarativo
- **Internacionalización (i18n)**: Soporte para múltiples idiomas
- **Accesibilidad**: Componentes accesibles incluidos

## 📁 Estructura del Proyecto

```
pyphonos/
├── core/              # Núcleo del framework
│   ├── app.py         # Clase base MobileApp
│   ├── navigator.py   # Sistema de navegación
│   ├── theme.py       # Sistema de temas
│   ├── animation.py   # Sistema de animaciones
│   └── ...
├── widgets/           # Componentes UI
│   ├── __init__.py    # Exporta widgets principales
│   ├── advanced.py    # Widgets avanzados
│   └── ...
├── renderer/          # Motor de renderizado
│   ├── canvas.py      # Canvas de dibujo
│   ├── colors.py      # Sistema de colores
│   ├── effects.py     # Efectos visuales
│   └── lighting.py    # Sistema de iluminación
├── events/            # Sistema de eventos
├── assets/            # Recursos (imágenes, fuentes, etc.)
├── interza.py         # Demo: Reproductor musical neumórfico
├── requirements.txt   # Dependencias
└── README.md          # Este archivo
```

## 🚀 Instalación

### Requisitos previos

- Python 3.7+
- pip

### Instalar dependencias

```bash
pip install -r requirements.txt
```

Las dependencias principales incluyen:
- `pysdl2>=0.9.14` - Bindings de SDL2
- `pysdl2-dll>=2.30.0` - DLLs de SDL2 precompiladas

## 💡 Uso Básico

### Crear una aplicación simple

```python
from core.app import MobileApp
from core.navigator import Screen
from widgets import Label, NeumorphicButton

class MiPantalla(Screen):
    def build(self):
        self.bg_color = Color(224, 229, 236, 255)
        
        titulo = Label(
            text="¡Hola Mundo!",
            x=100, y=100,
            size=20,
            color=Color(51, 51, 51, 255)
        )
        self.add_widget(titulo)

class MiApp(MobileApp):
    def on_start(self):
        self.navigator.push(MiPantalla())

if __name__ == "__main__":
    app = MiApp()
    app.run()
```

## 🎵 Demostración Incluida

El proyecto incluye una demostración completa de un reproductor musical con diseño neumórfico:

```bash
python interza.py
```

La demo muestra:
- Carátula de álbum circular con efecto neumórfico
- Controles de reproducción (play/pause, anterior, siguiente)
- Barra de progreso
- Control de volumen
- Animaciones e interacciones

## 🧪 Testing

Ejecutar los tests del sistema:

```bash
python test_systems.py
```

## 📂 Módulos Principales

### Core (`core/`)
- **MobileApp**: Clase base para aplicaciones
- **Screen**: Clase base para pantallas
- **Navigator**: Gestor de navegación entre pantallas
- **Theme**: Sistema de temas y estilos
- **Animation**: Sistema de animaciones
- **FormValidator**: Validación de formularios
- **i18n**: Internacionalización

### Widgets (`widgets/`)
- **NeumorphicWidget**: Widget base con estilo neumórfico
- **NeumorphicButton**: Botón con efectos neumórficos
- **NeumorphicContainer**: Contenedor con estilo neumórfico
- **Label**: Etiqueta de texto
- Y más componentes...

### Renderer (`renderer/`)
- **Canvas**: Sistema de dibujo
- **Color/Palette**: Manejo de colores
- **Effects**: Efectos visuales
- **Lighting**: Sistema de iluminación para efectos 3D
- **Icons**: Iconos integrados

### Events (`events/`)
- **Handler**: Manejador de eventos
- **Signals**: Sistema de señales

## 🎨 Sistema Neumórfico

El framework implementa un sistema de diseño neumórfico que simula elementos físicos con:
- **Elevación**: Controla la altura aparente del widget
- **Sombras**: Luces y sombras para crear profundidad
- **Bordes redondeados**: Para un look moderno y suave
- **Estados presionados**: Simulación de hundimiento al interactuar

Ejemplo de widget neumórfico:

```python
boton = NeumorphicButton(
    text="▶",
    x=150, y=440,
    width=80, height=80,
    border_radius=40,
    elevation=1.5,
    on_click=self.toggle_play
)
```

## 📝 Licencia

Este proyecto está bajo la licencia incluida en el archivo `LICENSE`.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Haz fork del repositorio
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📞 Soporte

Para issues o preguntas, por favor crea un issue en el repositorio.

---

**PyPhonOS** - Creando interfaces hermosas en Python 🐍✨
