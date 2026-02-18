from flask import Flask, render_template, request, jsonify, send_file
from dotenv import load_dotenv
import os
import json
from datetime import datetime
import random

load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# Base de données simple (en mémoire pour commencer)
ANIME_DATABASE = "animes.json"

def load_animes():
    """Charge les animes depuis le fichier JSON"""
    if os.path.exists(ANIME_DATABASE):
        with open(ANIME_DATABASE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_animes(animes):
    """Sauvegarde les animes dans un fichier JSON"""
    with open(ANIME_DATABASE, 'w', encoding='utf-8') as f:
        json.dump(animes, f, ensure_ascii=False, indent=2)

def generate_anime_ia(titre=""):
    """IA basique pour générer des animes"""
    genres = ["Action", "Romance", "Comédie", "Drame", "Fantaisie", "Mystère", "Thriller", "Sci-Fi"]
    studios = ["Studio A", "Studio B", "Studio C", "Studio D"]
    
    anime_titre = titre if titre else f"Anime {random.randint(1000, 9999)}"
    description_fr = f"Une histoire captivante qui vous plongera dans un univers fascinant. Suivez les aventures des personnages principaux à travers des rebondissements inattendus."
    
    return {
        "id": len(load_animes()) + 1,
        "titre": anime_titre,
        "description_fr": description_fr,
        "genre": random.choice(genres),
        "studio": random.choice(studios),
        "episodes": random.randint(12, 26),
        "annee": datetime.now().year,
        "date_ajout": datetime.now().isoformat()
    }

@app.route('/')
def home():
    """Page d'accueil"""
    animes = load_animes()
    return render_template('index.html', animes=animes, total=len(animes))

@app.route('/api/animes', methods=['GET'])
def get_animes():
    """Récupère tous les animes"""
    animes = load_animes()
    return jsonify(animes)

@app.route('/api/animes/generate', methods=['POST'])
def generate_anime():
    """Génère un nouvel anime avec l'IA basique"""
    data = request.json
    titre = data.get('titre', '')
    
    nouveau_anime = generate_anime_ia(titre)
    animes = load_animes()
    animes.append(nouveau_anime)
    save_animes(animes)
    
    return jsonify({
        "success": True,
        "message": f"Anime '{nouveau_anime['titre']}' généré avec succès!",
        "anime": nouveau_anime
    })

@app.route('/api/animes/<int:anime_id>', methods=['GET'])
def get_anime(anime_id):
    """Récupère un anime spécifique"""
    animes = load_animes()
    for anime in animes:
        if anime['id'] == anime_id:
            return jsonify(anime)
    return jsonify({"error": "Anime non trouvé"}), 404

@app.route('/api/animes/<int:anime_id>', methods=['DELETE'])
def delete_anime(anime_id):
    """Supprime un anime"""
    animes = load_animes()
    animes = [a for a in animes if a['id'] != anime_id]
    save_animes(animes)
    return jsonify({"success": True, "message": "Anime supprimé"})

@app.route('/api/animes/<int:anime_id>/watch', methods=['GET'])
def watch_anime(anime_id):
    """Affiche la page de visualisation"""
    animes = load_animes()
    anime = next((a for a in animes if a['id'] == anime_id), None)
    
    if not anime:
        return "Anime non trouvé", 404
    
    return render_template('watch.html', anime=anime)

@app.route('/api/animes/<int:anime_id>/download', methods=['GET'])
def download_anime(anime_id):
    """Prépare le téléchargement d'un anime"""
    animes = load_animes()
    anime = next((a for a in animes if a['id'] == anime_id), None)
    
    if not anime:
        return jsonify({"error": "Anime non trouvé"}), 404
    
    # Vous pouvez implémenter le téléchargement réel ici
    return jsonify({
        "success": True,
        "message": f"Téléchargement de '{anime['titre']}' en préparation...",
        "anime": anime
    })

@app.route('/about')
def about():
    """Page À propos"""
    return render_template('about.html')

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))