# setup_assets.py
import os
import urllib.request

def setup_pyphonos_assets():
    # 1. Crear carpetas
    folder = "assets/fonts"
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"Carpeta creada: {folder}")

    # 2. Nueva URL estable (Google Fonts)
    # Esta es una versión comprimida pero funcional de Roboto Regular
    font_url = "https://fonts.gstatic.com/s/roboto/v30/KFOmCnqEu92Fr1Mu4mxK.ttf"
    font_path = os.path.join(folder, "Roboto.ttf")

    # 3. Descargar con un User-Agent para evitar que Google nos bloquee
    print("Descargando fuente Roboto para PyPhonOS...")
    try:
        req = urllib.request.Request(
            font_url, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req) as response, open(font_path, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
        print(f"¡Éxito! Fuente guardada en: {font_path}")
    except Exception as e:
        print(f"Error al descargar: {e}")
        print("Intenta descargar manualmente 'Roboto-Regular.ttf' y ponlo en assets/fonts/Roboto.ttf")

if __name__ == "__main__":
    setup_pyphonos_assets()