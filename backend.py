from flask import Flask, request, jsonify
from flask_cors import CORS
import feedparser
import re
import requests
import os

app = Flask(__name__)
CORS(app)  # Permitir llamadas desde el frontend local


@app.route("/rss", methods=["GET"])
def get_rss():
    '''
    Usamos una petición de tipo `requests` para captura la información del RSS.

    Incluimos una cabecera (`headers`) para hacer ver al servidor al que enviamos una
    solicitud que actuamos como un navegador web.
    '''
    # Capturamos la URL solicitada
    rss_url = request.args.get("url")
    if not rss_url:
        return jsonify({"error": "Missing URL"}), 400

    # Definimos la cabecera de la solicitud
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; FeedReaderBot/1.0; +https://example.com/bot)"
    }

    # Ejecutamos la solicitud mediante 'requests.get'
    try:
        response = requests.get(rss_url, headers=headers, timeout=10)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
    except Exception as e:
        print(f"[ERROR] Al solicitar el feed: {e}")
        return jsonify({"error": "No se pudo leer el feed"}), 500

    # Inicializamos el diccionario a devolver, con valores por defecto 
    # para "title" y "link"
    result = {
        "feed": {
            "title": feed.feed.get("title", "Sin título"),
            "link": feed.feed.get("link", "")
        },
        "items": []
    }

    for entry in feed.entries[:20]:  # máximo 20 entradas
        thumbnail = ""

        # 1. media:thumbnail
        media_thumb = entry.get("media_thumbnail")
        if isinstance(media_thumb, list) and media_thumb and media_thumb[0].get("url"):
            thumbnail = media_thumb[0]["url"]

        # 2. media:content
        elif isinstance(entry.get("media_content"), list) and entry["media_content"]:
            thumbnail = entry["media_content"][0].get("url", "")

        # 3. enclosure
        elif entry.get("enclosures"):
            thumbnail = entry["enclosures"][0].get("href", "")

        # 4. imagen en HTML <description>
        raw_description = entry.get("description", "")
        if not thumbnail:
            match = re.search(r'<img[^>]+src="([^">]+)"', raw_description)
            if match:
                thumbnail = match.group(1)

        # Eliminar etiquetas HTML de la descripción
        clean_description = re.sub(r'<[^>]*>', '', raw_description)

        # Añadimos la entrada en la clave "items" del diccionario
        result["items"].append({
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "pubDate": entry.get("published", ""),
            "description": clean_description,
            "thumbnail": thumbnail
        })

    # Devolvemos el resultado en formato JSON
    return jsonify(result)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)
