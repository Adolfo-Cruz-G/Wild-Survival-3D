import urllib.request
import os

sounds = {
    "paso.wav": "https://github.com/pokeprotos/ursina/raw/master/ursina/assets/punch_strong.wav",
    "noche.wav": "https://github.com/pokeprotos/ursina/raw/master/ursina/assets/shutter.wav"
}

print("Descargando sonidos...")
for name, url in sounds.items():
    try:
        urllib.request.urlretrieve(url, name)
        print(f"Descargado: {name}")
    except Exception as e:
        print(f"Error descargando {name}: {e}")
