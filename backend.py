from flask import Flask, request, jsonify
from flask_cors import CORS
import feedparser
import re
import os

app = Flask(__name__)
CORS(app)  # Permitir llamadas desde el frontend local


@app.route("/rss", methods=["GET"])
def get_rss():
    rss_url = request.args.get("url")
    if not rss_url:
        return jsonify({"error": "Missing URL"}), 400

    feed = feedparser.parse(rss_url)

    result = {
        "feed": {
            "title": feed.feed.get("title", "Sin título")
        },
        "items": []
    }

    for entry in feed.entries[:10]:  # máximo 10 entradas
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

        result["items"].append({
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "pubDate": entry.get("published", ""),
            "description": clean_description,
            "thumbnail": thumbnail
        })

    return jsonify(result)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
