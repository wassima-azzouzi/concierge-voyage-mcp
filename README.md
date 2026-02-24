# 🧳 Concierge Voyage MCP

## 📝 Description
Concierge Voyage MCP est une application de planification de voyage interactive développée en Python avec Streamlit. Elle permet aux utilisateurs de rechercher des vols, de consulter la météo des destinations, de calculer des itinéraires routiers et de trouver des services à proximité (hôtels, restaurants) autour des aéroports.

L'objectif est de centraliser toutes les informations nécessaires pour préparer un voyage (Vols + Météo + Transport + Services) dans une interface unique et simple.

## ✨ Fonctionnalités Principales

### 1. ✈️ Recherche de Vols
*   Recherche de vols via l'API **Amadeus**.
*   Saisie flexible (Code IATA ou Nom de ville).
*   Affichage des offres avec prix, horaires, compagnies aériennes et escales.

### 2. 🌤️ Météo & Services
*   **Météo** : Affichage de la météo actuelle et des prévisions sur 5 jours pour les villes de départ et d'arrivée (API **OpenWeather**).
*   **Services à Proximité** : Liste automatique des **Hôtels, Restaurants et Cafés** situés autour de l'aéroport sélectionné (via **Overpass API / OpenStreetMap**).

### 3. 🗺️ Trajets & Navigation
*   **Calcul d'Itinéraire** : Route voiture entre le point de départ et le point d'arrivée (API **OpenRouteService**).
*   **Visualisation** : Carte interactive (**Folium**) affichant le tracé du trajet en bleu et des marqueurs pour les points d'intérêt.
*   **Géocodage** : Conversion automatique des adresses en coordonnées GPS.

### 4. 🌐 Rôle du MCP (Model Context Protocol)
Ce système est conçu selon l'architecture **MCP (Model Context Protocol)**. Chaque module (Vols, Météo, Trajets) agit comme un **outil autonome** pouvant être connecté à une Intelligence Artificielle.

Bien que l'application fonctionne ici en mode "Direct" (interface graphique manuelle), cette structure modulaire permettrait à un Assistant IA (comme Gemini ou Claude) d'utiliser ces mêmes fonctions pour répondre à des demandes complexes de manière autonome, standardisant ainsi l'interaction entre le modèle de langage et les services externes.

## 🛠️ Technologies & Outils Utilisés

*   **Langage** : Python 3.10+
*   **Interface Utilisateur** : [Streamlit](https://streamlit.io/)
*   **Cartographie** : [Folium](https://python-visualization.github.io/folium/) & `streamlit-folium`
*   **APIs Externes** :
    *   **Amadeus** (Vols)
    *   **OpenWeather** (Météo)
    *   **OpenRouteService** (Itinéraires & Géocodage)
    *   **Overpass API** (Points d'intérêt OSM)
*   **Gestion d'Environnement** : `python-dotenv`

## 🚀 Installation & Lancement

### Préoccupations
*   Python installé sur votre machine.
*   Clés API pour Amadeus, OpenWeather et OpenRouteService.

### 1. Installation des dépendances
Ouvrez un terminal dans le dossier du projet et exécutez :
```bash
pip install -r requirements.txt
```

### 2. Configuration (`.env`)
Créez un fichier `.env` à la racine et ajoutez vos clés API :
```env
AMADEUS_API_KEY=votre_cle_amadeus
AMADEUS_API_SECRET=votre_secret_amadeus
OPENWEATHER_API_KEY=votre_cle_openweather
ORS_API_KEY=votre_cle_openrouteservice
```

### 3. Lancement
Lancez l'application avec le script de démarrage automatique :
```bash
python run.py
```
Le script va vérifier les dépendances et lancer l'application dans votre navigateur par défaut (généralement sur `http://localhost:8501`).

## 📂 Structure du Projet
*   `app_direct.py` : Code principal de l'application Streamlit.
*   `run.py` : Script de lancement (vérifie l'environnement et lance Streamlit).
*   `requirements.txt` : Liste des bibliothèques Python requises.
*   `.env` : Fichier de configuration des clés API.
