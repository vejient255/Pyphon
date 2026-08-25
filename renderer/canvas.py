# renderer/canvas.py
import sdl2
import sdl2.sdlttf
import sdl2.sdlimage # Librería para PNG/JPG
import os
import sys
import math
import ctypes

from renderer.lighting import LightingEngine

class Canvas:
    def __init__(self, window_instance):
        """
        Constructor del sistema de renderizado.
        Optimizado para Android usando aceleración por hardware (GPU).
        """
        self.win = window_instance
        self.renderer = window_instance.renderer.renderer
        
        # Inicializar fuentes TrueType (TTF)
        if sdl2.sdlttf.TTF_Init() == -1:
            print("Error inicializando SDL_ttf")
            
        # Inicializar soporte de imágenes (PNG y JPG)
        flags = sdl2.sdlimage.IMG_INIT_PNG | sdl2.sdlimage.IMG_INIT_JPG
        if (sdl2.sdlimage.IMG_Init(flags) & flags) != flags:
            print("Error inicializando SDL_image")

        # CACHÉ CRÍTICA: Guardamos texturas para que la GPU no trabaje doble
        self._font_cache = {}
        self._image_cache = {} 
        self._text_cache = {} 
        self._shape_cache = {} # Nueva caché para formas (esquinas AA, sombras)
        
        # Cola de dibujo de superposición (Overlays)
        self.overlays = []

    def draw_overlays(self):
        """Ejecuta todos los comandos de dibujo registrados en la capa superior."""
        for draw_func in self.overlays:
            try:
                draw_func()
            except Exception as e:
                print(f"Error en overlay: {e}")
        self.overlays.clear()

    def get_asset_path(self, relative_path):
        """
        Ajusta la ruta de los archivos para que funcione en Windows 
        y dentro de la estructura interna de una APK de Android.
        """
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        elif hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            # Sube dos niveles desde renderer/ para llegar a la raíz
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        return os.path.normpath(os.path.join(base_path, relative_path))

    @property
    def width(self):
        """Obtiene el ancho actual de la pantalla del dispositivo."""
        return self.win.ancho

    @property
    def height(self):
        """Obtiene el alto actual de la pantalla del dispositivo."""
        return self.win.alto

    def measure_text(self, text, size=20, font_name="Roboto-Regular.ttf"):
        """
        Mide las dimensiones de un texto sin renderizarlo.
        Útil para tipografía dinámica y ajuste automático de tamaños.

        Returns:
            (width, height) en píxeles, o (0, 0) si hay error.
        """
        if not text:
            return (0, 0)
        font_path = self.get_asset_path(os.path.join("assets", "fonts", font_name))
        font_key = f"{font_path}_{size}"

        if font_key not in self._font_cache:
            if not os.path.exists(font_path):
                return (0, 0)
            font = sdl2.sdlttf.TTF_OpenFont(font_path.encode('utf-8'), size)
            if not font:
                return (0, 0)
            self._font_cache[font_key] = font

        font = self._font_cache[font_key]
        tw = ctypes.c_int(0)
        th = ctypes.c_int(0)
        sdl2.sdlttf.TTF_SizeUTF8(font, str(text).encode('utf-8'), ctypes.byref(tw), ctypes.byref(th))
        return (tw.value, th.value)

    def clear(self, color_hex=0xFEF7FF):
        """Limpia el frame con un color moderno de fondo (Soft Lavender White)."""
        r, g, b = self._hex_to_rgb(color_hex)
        sdl2.SDL_SetRenderDrawColor(self.renderer, r, g, b, 255)
        sdl2.SDL_RenderClear(self.renderer)

    def draw_image(self, relative_path, x, y, w=None, h=None):
        """Dibuja imágenes con filtrado de alta calidad."""
        path = self.get_asset_path(relative_path)
        
        if path not in self._image_cache:
            texture = sdl2.sdlimage.IMG_LoadTexture(self.renderer, path.encode('utf-8'))
            if not texture: return
            
            tw, th = sdl2.c_int(), sdl2.c_int()
            sdl2.SDL_QueryTexture(texture, None, None, tw, th)
            self._image_cache[path] = (texture, tw.value, th.value)
        
        texture, orig_w, orig_h = self._image_cache[path]
        render_w = w if w is not None else orig_w
        render_h = h if h is not None else orig_h
        
        dst_rect = sdl2.SDL_Rect(int(x), int(y), int(render_w), int(render_h))
        sdl2.SDL_RenderCopy(self.renderer, texture, None, dst_rect)

    def draw_image_advanced(self, relative_path, x, y, w, h, scale_mode="contain", alpha=255, border_radius=0):
        """
        Dibuja una imagen con opciones avanzadas de escalado (cover, contain, fill)
        y opacidad. El redondeo de bordes requeriría un render target complejo o stencil,
        por simplicidad dibujaremos la imagen ajustada.
        """
        path = self.get_asset_path(relative_path)
        
        if path not in self._image_cache:
            if not os.path.exists(path):
                # Fallback to absolute if purely passed
                if os.path.exists(relative_path):
                    path = relative_path
                else:
                    return
            texture = sdl2.sdlimage.IMG_LoadTexture(self.renderer, path.encode('utf-8'))
            if not texture: return
            
            tw, th = sdl2.c_int(), sdl2.c_int()
            sdl2.SDL_QueryTexture(texture, None, None, tw, th)
            self._image_cache[path] = (texture, tw.value, th.value)
        
        texture, tex_w, tex_h = self._image_cache[path]
        
        # Aplicar opacidad
        if alpha < 255:
            sdl2.SDL_SetTextureBlendMode(texture, sdl2.SDL_BLENDMODE_BLEND)
            sdl2.SDL_SetTextureAlphaMod(texture, alpha)
        else:
            sdl2.SDL_SetTextureAlphaMod(texture, 255)

        src_rect = None
        dst_rect = sdl2.SDL_Rect(int(x), int(y), int(w), int(h))

        if scale_mode == "fill":
            pass # src_rect = None, dst_rect = full box
            
        elif scale_mode == "contain":
            aspect_tex = tex_w / tex_h
            aspect_box = w / h
            if aspect_tex > aspect_box:
                # La imagen es más ancha que la caja
                render_w = w
                render_h = int(w / aspect_tex)
                oy = (h - render_h) // 2
                dst_rect = sdl2.SDL_Rect(int(x), int(y + oy), int(render_w), int(render_h))
            else:
                # La imagen es más alta que la caja
                render_h = h
                render_w = int(h * aspect_tex)
                ox = (w - render_w) // 2
                dst_rect = sdl2.SDL_Rect(int(x + ox), int(y), int(render_w), int(render_h))
                
        elif scale_mode == "cover":
            aspect_tex = tex_w / tex_h
            aspect_box = w / h
            if aspect_tex > aspect_box:
                # Cortar izquierda y derecha
                crop_w = int(tex_h * aspect_box)
                crop_x = (tex_w - crop_w) // 2
                src_rect = sdl2.SDL_Rect(crop_x, 0, crop_w, tex_h)
            else:
                # Cortar arriba y abajo
                crop_h = int(tex_w / aspect_box)
                crop_y = (tex_h - crop_h) // 2
                src_rect = sdl2.SDL_Rect(0, crop_y, tex_w, crop_h)

        sdl2.SDL_RenderCopy(self.renderer, texture, src_rect, dst_rect)

    def draw_text(self, text, x, y, color_hex, size=20, font_name="Roboto-Regular.ttf"):
        """
        Dibuja texto con renderizado UTF-8 Blended.
        Soporta caracteres especiales (ñ, á, etc) y mantiene alta nitidez.
        """
        if not text: return

        # Identificador único para el texto en caché
        text_key = f"{text}_{color_hex}_{size}_{font_name}"
        
        if text_key in self._text_cache:
            texture, w, h = self._text_cache[text_key]
        else:
            r, g, b = self._hex_to_rgb(color_hex)
            sdl_color = sdl2.SDL_Color(r, g, b, 255) # Añadido canal alpha 255
            font_path = self.get_asset_path(os.path.join("assets", "fonts", font_name))
            font_key = f"{font_path}_{size}"

            if font_key not in self._font_cache:
                if not os.path.exists(font_path): 
                    print(f"Error: No se encontró la fuente en {font_path}")
                    return
                font = sdl2.sdlttf.TTF_OpenFont(font_path.encode('utf-8'), size)
                if not font: return
                self._font_cache[font_key] = font
            
            font = self._font_cache[font_key]
            
            # --- MEJORA CRÍTICA PARA CALIDAD Y CARACTERES ESPECIALES ---
            # Usamos TTF_RenderUTF8_Blended para soportar Unicode y Anti-Aliasing real.
            surface = sdl2.sdlttf.TTF_RenderUTF8_Blended(font, str(text).encode('utf-8'), sdl_color)
            if not surface: return
            
            texture = sdl2.SDL_CreateTextureFromSurface(self.renderer, surface)
            w, h = surface.contents.w, surface.contents.h
            sdl2.SDL_FreeSurface(surface)
            
            # Guardamos en caché para no recrear el texto en cada frame
            self._text_cache[text_key] = (texture, w, h)

        dst_rect = sdl2.SDL_Rect(int(x), int(y), w, h)
        sdl2.SDL_RenderCopy(self.renderer, texture, None, dst_rect)

    def draw_rect(self, x, y, w, h, color_hex, alpha=255):
        """Rectángulo sólido con soporte para canal Alpha y Blending."""
        r, g, b = self._hex_to_rgb(color_hex)
        sdl2.SDL_SetRenderDrawBlendMode(self.renderer, sdl2.SDL_BLENDMODE_BLEND)
        sdl2.SDL_SetRenderDrawColor(self.renderer, r, g, b, alpha)
        rect = sdl2.SDL_Rect(int(x), int(y), int(w), int(h))
        sdl2.SDL_RenderFillRect(self.renderer, rect)

    def write_pixel(self, x, y, color_hex, alpha=255):
        """Dibuja un píxel individual con soporte para Alpha."""
        r, g, b = self._hex_to_rgb(color_hex)
        sdl2.SDL_SetRenderDrawColor(self.renderer, r, g, b, alpha)
        sdl2.SDL_RenderDrawPoint(self.renderer, int(x), int(y))

    def draw_circle(self, x, y, r, color_hex, alpha=255):
        """
        Dibuja un círculo completo con Anti-Aliasing.
        Optimizado para usar la caché de esquinas mediante draw_rounded_rect.
        """
        # Un círculo es equivalente a un rectángulo redondeado con radio = ancho/2
        self.draw_rounded_rect(x - r, y - r, r * 2, r * 2, r, color_hex, alpha)

    def draw_rounded_rect(self, x, y, w, h, r, color_hex, alpha=255):
        """
        Dibuja un rectángulo con bordes redondeados OPTIMIZADO mediante caché.
        No recalcula píxeles en cada cuadro, usa blitting de texturas.
        """
        r_val = int(min(r, w/2, h/2))
        if r_val <= 0:
            self.draw_rect(x, y, w, h, color_hex, alpha)
            return

        # 1. Dibujar el cuerpo principal (3 rectángulos para evitar solapamientos)
        self.draw_rect(x + r_val, y, w - 2 * r_val, h, color_hex, alpha)         # Centro vertical
        self.draw_rect(x, y + r_val, r_val, h - 2 * r_val, color_hex, alpha)      # Ala izquierda
        self.draw_rect(x + w - r_val, y + r_val, r_val, h - 2 * r_val, color_hex, alpha) # Ala derecha
        
        # 2. Obtener/Crear textura de la esquina mediante caché
        cache_key = f"corner_{r_val}_{color_hex}_{alpha}"
        if cache_key not in self._shape_cache:
            self._shape_cache[cache_key] = self._create_corner_texture(r_val, color_hex, alpha)
        
        tex = self._shape_cache[cache_key]
        
        # 3. Dibujar las 4 esquinas copiando la textura
        # El cuarto de círculo se rota/voltea para cada esquina
        self._blit_corner(tex, x, y, r_val, flip_h=False, flip_v=False)             # UL
        self._blit_corner(tex, x + w - r_val, y, r_val, flip_h=True, flip_v=False)  # UR
        self._blit_corner(tex, x, y + h - r_val, r_val, flip_h=False, flip_v=True)  # LL
        self._blit_corner(tex, x + w - r_val, y + h - r_val, r_val, flip_h=True, flip_v=True) # LR

    def _blit_corner(self, texture, x, y, r, flip_h=False, flip_v=False):
        """Helper para copiar una textura de esquina con volteo opcional."""
        dst = sdl2.SDL_Rect(int(x), int(y), r, r)
        flip = sdl2.SDL_FLIP_NONE
        if flip_h: flip |= sdl2.SDL_FLIP_HORIZONTAL
        if flip_v: flip |= sdl2.SDL_FLIP_VERTICAL
        sdl2.SDL_RenderCopyEx(self.renderer, texture, None, dst, 0.0, None, flip)

    def _create_corner_texture(self, r, color_hex, alpha):
        """Genera una textura de un cuarto de círculo con Anti-Aliasing."""
        # Creamos una superficie con canal Alpha
        surface = sdl2.SDL_CreateRGBSurfaceWithFormat(0, r, r, 32, sdl2.SDL_PIXELFORMAT_RGBA32)
        red, g, b = self._hex_to_rgb(color_hex)
        
        rad_sq = r * r
        # Dibujamos píxel a píxel el cuarto de círculo (solo una vez)
        for dy in range(r):
            for dx in range(r):
                # Reposicionar para que el centro sea la esquina opuesta (r, r)
                # para generar el cuarto superior izquierdo
                dist_sq = (r-1-dx)**2 + (r-1-dy)**2
                
                if dist_sq <= rad_sq:
                    dist = math.sqrt(dist_sq)
                    if dist > r - 1.0:
                        smooth_alpha = int(alpha * (r - dist))
                    else:
                        smooth_alpha = alpha
                    
                    if smooth_alpha > 0:
                        # Escribir directamente en la superficie (RGBA) utilizando ctypes
                        pixel_ptr = ctypes.cast(surface.contents.pixels, ctypes.POINTER(ctypes.c_uint8))
                        idx = (dy * surface.contents.pitch) + (dx * 4)
                        pixel_ptr[idx] = red
                        pixel_ptr[idx+1] = g
                        pixel_ptr[idx+2] = b
                        pixel_ptr[idx+3] = smooth_alpha
        
        texture = sdl2.SDL_CreateTextureFromSurface(self.renderer, surface)
        sdl2.SDL_FreeSurface(surface)
        return texture

    def draw_shadow(self, x, y, w, h, radius=16, intensity=35):
        """
        Dibuja una sombra perimetral suave OPTIMIZADA.
        Utiliza una textura de sombra genérica en caché para evitar bucles pesados.
        """
        cache_key = f"shadow_blob_{radius}_{intensity}"
        if cache_key not in self._shape_cache:
            self._shape_cache[cache_key] = self._create_shadow_texture(radius, intensity)
        
        tex = self._shape_cache[cache_key]
        
        # Dibujamos la sombra mediante 9 partes escaladas (9-slice logic simplificado)
        # Esquinas
        self._blit_corner(tex, x - radius, y - radius + 2, radius, False, False) # UL
        self._blit_corner(tex, x + w, y - radius + 2, radius, True, False)       # UR
        self._blit_corner(tex, x - radius, y + h + 2, radius, False, True)       # LL
        self._blit_corner(tex, x + w, y + h + 2, radius, True, True)            # LR
        
        # Lados (estirados)
        self.draw_image_stretched(tex, x, y - radius + 2, w, radius, side="top")
        self.draw_image_stretched(tex, x, y + h + 2, w, radius, side="bottom")
        self.draw_image_stretched(tex, x - radius, y + 2, radius, h, side="left")
        self.draw_image_stretched(tex, x + w, y + 2, radius, h, side="right")
        
        # Centro de la sombra
        self.draw_rect(x, y + 2, w, h, 0x000000, alpha=intensity)

    def draw_image_stretched(self, texture, x, y, w, h, side):
        """Dibuja una parte específica de la textura estirada."""
        rect = sdl2.SDL_Rect(int(x), int(y), int(w), int(h))
        sdl2.SDL_RenderCopy(self.renderer, texture, None, rect)

    def _create_shadow_texture(self, r, intensity):
        """Genera un patrón de sombra radial (un cuarto) para la caché."""
        return self._create_corner_texture(r, 0x000000, intensity)
    
    def draw_neumorphic_surface(self, x, y, w, h, border_radius, base_color, 
                                 elevation=1.0, pressed=False, light_angle=None):
        """
        Dibuja una superficie con efecto neumórfico completo usando el motor de iluminación.
        Maneja automáticamente las dos sombras (clara y oscura) para crear volumen real.
        
        Args:
            x, y: Posición del widget
            w, h: Dimensiones
            border_radius: Radio de bordes redondeados
            base_color: Color base (hex o Color)
            elevation: Altura simulada (0.5 a 3.0) - mayor = más relieve
            pressed: Si True, invierte sombras para efecto hundido
            light_angle: Ángulo de luz personalizado (default: 315°)
        """
        # Calcular sombras usando el motor de iluminación
        if pressed:
            light_shadow, dark_shadow, offset_x, offset_y = LightingEngine.calculate_pressed_shadows(
                base_color, depth=elevation
            )
        else:
            light_shadow, dark_shadow, offset_x, offset_y = LightingEngine.calculate_shadows(
                base_color, elevation=elevation, light_angle=light_angle
            )
        
        abs_x, abs_y = int(x), int(y)
        
        # 1. Dibujar sombra oscura (la que está más lejos del fondo)
        shadow_offset = 3 + int(elevation * 2)
        if border_radius > 0:
            self.draw_rounded_rect(
                abs_x + shadow_offset, abs_y + shadow_offset, w, h,
                border_radius, dark_shadow, alpha=min(80, int(40 * elevation))
            )
        else:
            self.draw_rect(
                abs_x + shadow_offset, abs_y + shadow_offset, w, h,
                dark_shadow, alpha=min(80, int(40 * elevation))
            )
        
        # 2. Dibujar sombra clara (highlight)
        highlight_offset = max(0, shadow_offset - 2)
        if border_radius > 0:
            self.draw_rounded_rect(
                abs_x - highlight_offset, abs_y - highlight_offset, w, h,
                border_radius, light_shadow, alpha=min(60, int(30 * elevation))
            )
        else:
            self.draw_rect(
                abs_x - highlight_offset, abs_y - highlight_offset, w, h,
                light_shadow, alpha=min(60, int(30 * elevation))
            )
        
        # 3. Dibujar superficie base (encima de las sombras)
        if border_radius > 0:
            self.draw_rounded_rect(abs_x, abs_y, w, h, border_radius, base_color)
        else:
            self.draw_rect(abs_x, abs_y, w, h, base_color)
        
        return (light_shadow, dark_shadow)

    def _hex_to_rgb(self, color_hex):
        """Convierte enteros o hexadecimales a formato RGB compatible con SDL2."""
        try:
            c_val = int(color_hex)
            r = (c_val >> 16) & 0xFF
            g = (c_val >> 8) & 0xFF
            b = c_val & 0xFF
            return r, g, b
        except:
            return 255, 255, 255