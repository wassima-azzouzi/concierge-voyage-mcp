import streamlit as st
from amadeus import Client, ResponseError
from datetime import datetime, date, timedelta
import os
import requests
import json
import json
from dotenv import load_dotenv
import folium
from streamlit_folium import st_folium

load_dotenv()

# Configuration de la page
st.set_page_config(
    page_title="Concierge Voyage Direct",
    page_icon="🧳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Mobile & App Style



# ==================== CONFIGURATION DES APIS ====================

# Initialisation du client Amadeus
try:
    amadeus = Client(
        client_id=st.secrets.get("AMADEUS_API_KEY") or os.getenv("AMADEUS_API_KEY"),
        client_secret=st.secrets.get("AMADEUS_API_SECRET") or os.getenv("AMADEUS_API_SECRET")
    )
except Exception as e:
    amadeus = None

# Clés API (à configurer dans .streamlit/secrets.toml ou variables d'environnement)
# Clés API (à configurer dans .streamlit/secrets.toml ou variables d'environnement)
OPENWEATHER_API_KEY = st.secrets.get("OPENWEATHER_API_KEY") or os.getenv("OPENWEATHER_API_KEY")
ORS_API_KEY = st.secrets.get("ORS_API_KEY") or os.getenv("ORS_API_KEY")

# ==================== BASE DE DONNÉES AÉROPORTS ====================

AIRPORTS_DB = [
    # Maroc
    {"code": "RBA", "city": "Rabat", "country": "Maroc", "name": "Rabat-Salé", "lat": 34.0515, "lon": -6.7515, "keywords": ["rabat", "sale", "salé"]},
    {"code": "CMN", "city": "Casablanca", "country": "Maroc", "name": "Mohammed V", "lat": 33.3675, "lon": -7.5898, "keywords": ["casablanca", "casa", "mohammed"]},
    {"code": "RAK", "city": "Marrakech", "country": "Maroc", "name": "Menara", "lat": 31.6069, "lon": -8.0363, "keywords": ["marrakech", "marrakesh"]},
    {"code": "FEZ", "city": "Fès", "country": "Maroc", "name": "Saïss", "lat": 33.9273, "lon": -4.9779, "keywords": ["fes", "fès", "fez"]},
    {"code": "TNG", "city": "Tanger", "country": "Maroc", "name": "Ibn Battouta", "lat": 35.7269, "lon": -5.9169, "keywords": ["tanger", "tangier"]},
    {"code": "AGA", "city": "Agadir", "country": "Maroc", "name": "Al Massira", "lat": 30.3250, "lon": -9.4131, "keywords": ["agadir"]},
    {"code": "OUD", "city": "Oujda", "country": "Maroc", "name": "Angads", "lat": 34.7867, "lon": -1.9236, "keywords": ["oujda"]},
    {"code": "NDR", "city": "Nador", "country": "Maroc", "name": "El Aroui", "lat": 34.9888, "lon": -3.0282, "keywords": ["nador"]},
    {"code": "TTU", "city": "Tétouan", "country": "Maroc", "name": "Sania Ramel", "lat": 35.5944, "lon": -5.3200, "keywords": ["tetouan", "tétouan"]},
    {"code": "EUN", "city": "Laâyoune", "country": "Maroc", "name": "Hassan I", "lat": 27.1517, "lon": -13.2192, "keywords": ["laayoune", "laâyoune", "el aaiun"]},
    {"code": "VIL", "city": "Dakhla", "country": "Maroc", "name": "Dakhla", "lat": 23.7181, "lon": -15.9350, "keywords": ["dakhla"]},
    {"code": "ESU", "city": "Essaouira", "country": "Maroc", "name": "Mogador", "lat": 31.3975, "lon": -9.6817, "keywords": ["essaouira"]},
    {"code": "OZZ", "city": "Ouarzazate", "country": "Maroc", "name": "Ouarzazate", "lat": 30.9394, "lon": -6.9094, "keywords": ["ouarzazate"]},
    
    # France
    {"code": "CDG", "city": "Paris", "country": "France", "name": "Charles de Gaulle", "lat": 49.0097, "lon": 2.5479, "keywords": ["paris", "cdg", "charles de gaulle", "roissy"]},
    {"code": "ORY", "city": "Paris", "country": "France", "name": "Orly", "lat": 48.7233, "lon": 2.3794, "keywords": ["paris", "orly"]},
    {"code": "LYS", "city": "Lyon", "country": "France", "name": "Saint-Exupéry", "lat": 45.7256, "lon": 5.0811, "keywords": ["lyon", "saint exupery"]},
    {"code": "MRS", "city": "Marseille", "country": "France", "name": "Provence", "lat": 43.4367, "lon": 5.2150, "keywords": ["marseille"]},
    {"code": "NCE", "city": "Nice", "country": "France", "name": "Côte d'Azur", "lat": 43.6584, "lon": 7.2158, "keywords": ["nice", "cote d'azur"]},
    {"code": "TLS", "city": "Toulouse", "country": "France", "name": "Blagnac", "lat": 43.6291, "lon": 1.3638, "keywords": ["toulouse"]},
    {"code": "BOD", "city": "Bordeaux", "country": "France", "name": "Mérignac", "lat": 44.8283, "lon": -0.7156, "keywords": ["bordeaux"]},
    {"code": "NTE", "city": "Nantes", "country": "France", "name": "Atlantique", "lat": 47.1532, "lon": -1.6107, "keywords": ["nantes"]},
    
    # Europe
    {"code": "LHR", "city": "Londres", "country": "Royaume-Uni", "name": "Heathrow", "lat": 51.4700, "lon": -0.4543, "keywords": ["londres", "london", "heathrow"]},
    {"code": "LGW", "city": "Londres", "country": "Royaume-Uni", "name": "Gatwick", "lat": 51.1537, "lon": -0.1821, "keywords": ["londres", "london", "gatwick"]},
    {"code": "MAD", "city": "Madrid", "country": "Espagne", "name": "Barajas", "lat": 40.4983, "lon": -3.5676, "keywords": ["madrid", "barajas"]},
    {"code": "BCN", "city": "Barcelone", "country": "Espagne", "name": "El Prat", "lat": 41.2974, "lon": 2.0833, "keywords": ["barcelone", "barcelona"]},
    {"code": "LIS", "city": "Lisbonne", "country": "Portugal", "name": "Humberto Delgado", "lat": 38.7813, "lon": -9.1359, "keywords": ["lisbonne", "lisbon", "lisboa"]},
    {"code": "FCO", "city": "Rome", "country": "Italie", "name": "Fiumicino", "lat": 41.8003, "lon": 12.2389, "keywords": ["rome", "fiumicino", "leonardo da vinci"]},
    {"code": "MXP", "city": "Milan", "country": "Italie", "name": "Malpensa", "lat": 45.6306, "lon": 8.7281, "keywords": ["milan", "malpensa"]},
    {"code": "BER", "city": "Berlin", "country": "Allemagne", "name": "Brandebourg", "lat": 52.3667, "lon": 13.5033, "keywords": ["berlin", "brandebourg", "brandenburg"]},
    {"code": "FRA", "city": "Francfort", "country": "Allemagne", "name": "Frankfurt", "lat": 50.0379, "lon": 8.5622, "keywords": ["francfort", "frankfurt"]},
    {"code": "AMS", "city": "Amsterdam", "country": "Pays-Bas", "name": "Schiphol", "lat": 52.3105, "lon": 4.7683, "keywords": ["amsterdam", "schiphol"]},
    {"code": "BRU", "city": "Bruxelles", "country": "Belgique", "name": "Zaventem", "lat": 50.9010, "lon": 4.4844, "keywords": ["bruxelles", "brussels", "zaventem"]},
    {"code": "GVA", "city": "Genève", "country": "Suisse", "name": "Cointrin", "lat": 46.2381, "lon": 6.1089, "keywords": ["geneve", "genève", "geneva"]},
    {"code": "ZRH", "city": "Zurich", "country": "Suisse", "name": "Zurich", "lat": 47.4647, "lon": 8.5492, "keywords": ["zurich", "zürich"]},
    
    # International
    {"code": "JFK", "city": "New York", "country": "USA", "name": "John F. Kennedy", "lat": 40.6413, "lon": -73.7781, "keywords": ["new york", "jfk", "kennedy"]},
    {"code": "EWR", "city": "New York", "country": "USA", "name": "Newark", "lat": 40.6895, "lon": -74.1745, "keywords": ["new york", "newark"]},
    {"code": "DXB", "city": "Dubai", "country": "UAE", "name": "Dubai International", "lat": 25.2532, "lon": 55.3657, "keywords": ["dubai", "dubaï"]},
    {"code": "IST", "city": "Istanbul", "country": "Turquie", "name": "Istanbul Airport", "lat": 41.2753, "lon": 28.7519, "keywords": ["istanbul", "constantinople"]},
    {"code": "DOH", "city": "Doha", "country": "Qatar", "name": "Hamad International", "lat": 25.2731, "lon": 51.6081, "keywords": ["doha"]},
    {"code": "AUH", "city": "Abu Dhabi", "country": "UAE", "name": "Zayed International", "lat": 24.4330, "lon": 54.6511, "keywords": ["abu dhabi", "abou dabi"]},
    {"code": "CAI", "city": "Le Caire", "country": "Egypte", "name": "Cairo International", "lat": 30.1219, "lon": 31.4056, "keywords": ["le caire", "cairo", "le cairo"]},
    {"code": "TUN", "city": "Tunis", "country": "Tunisie", "name": "Carthage", "lat": 36.8510, "lon": 10.2272, "keywords": ["tunis", "carthage"]},
    {"code": "ALG", "city": "Alger", "country": "Algérie", "name": "Houari Boumediene", "lat": 36.6910, "lon": 3.2154, "keywords": ["alger", "algiers"]},
]

# ==================== FONCTIONS UTILITAIRES ====================

def get_airport_by_code(code):
    """Récupère les infos d'un aéroport par son code IATA."""
    code = code.upper()
    for airport in AIRPORTS_DB:
        if airport["code"] == code:
            return airport
    return None

def get_airport_suggestions(query, max_results=10):
    """Retourne les suggestions d'aéroports."""
    if not query or len(query) < 1:
        popular_codes = ["RBA", "CMN", "RAK", "FEZ", "TNG", "CDG", "ORY", "LHR", "MAD", "BCN"]
        return [a for a in AIRPORTS_DB if a["code"] in popular_codes][:max_results]
    
    query = query.lower().strip()
    matches = []
    
    for airport in AIRPORTS_DB:
        score = 0
        
        if airport["code"].lower() == query:
            score = 1000
        elif airport["code"].lower().startswith(query):
            score = 500
        elif query in airport["code"].lower():
            score = 400
            
        if airport["city"].lower() == query:
            score = 300
        elif airport["city"].lower().startswith(query):
            score = 200
        elif query in airport["city"].lower():
            score = 100
            
        if query in airport["country"].lower():
            score = 50
            
        if query in airport["name"].lower():
            score = 80
            
        for keyword in airport["keywords"]:
            if keyword == query:
                score = 250
            elif keyword.startswith(query):
                score = 150
            elif query in keyword:
                score = 75
        
        if score > 0:
            matches.append({**airport, "score": score})
    
    matches.sort(key=lambda x: x["score"], reverse=True)
    return [{k: v for k, v in m.items() if k != "score"} for m in matches[:max_results]]

def format_airport_option(airport):
    """Formate l'affichage d'un aéroport."""
    return f"{airport['code']} - {airport['city']} ({airport['country']}) - {airport['name']}"

def get_iata_code_from_selection(selection_string):
    """Extrait le code IATA d'une sélection."""
    if not selection_string:
        return None
    return selection_string.split(" - ")[0] if " - " in selection_string else selection_string.upper()

# ==================== FONCTIONS MÉTÉO ====================

def get_weather_data(lat, lon, city_name):
    """Récupère les données météo via OpenWeatherMap."""
    if not OPENWEATHER_API_KEY:
        return {"error": "Clé API OpenWeather non configurée"}
    
    try:
        # Météo actuelle
        current_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric&lang=fr"
        current_response = requests.get(current_url, timeout=10)
        current_data = current_response.json()
        
        # Prévisions 5 jours
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric&lang=fr"
        forecast_response = requests.get(forecast_url, timeout=10)
        forecast_data = forecast_response.json()
        
        if current_response.status_code == 200 and forecast_response.status_code == 200:
            return {
                "current": current_data,
                "forecast": forecast_data,
                "success": True
            }
        else:
            error_msg = current_data.get('message', 'Erreur inconnue')
            return {"error": f"Erreur météo: {error_msg}"}
            
    except Exception as e:
        return {"error": f"Erreur de connexion: {str(e)}"}

def get_weather_icon_url(icon_code):
    """Retourne l'URL de l'icône météo."""
    return f"https://openweathermap.org/img/wn/{icon_code}@2x.png"

def display_weather_card(weather_data, city_name, is_destination=False):
    """Affiche une carte météo stylisée."""
    if "error" in weather_data:
        st.error(weather_data["error"])
        return
    
    current = weather_data.get("current", {})
    main = current.get("main", {})
    weather = current.get("weather", [{}])[0]
    wind = current.get("wind", {})
    
    emoji = "🛬" if is_destination else "🛫"
    title_color = "#e74c3c" if is_destination else "#3498db"
    
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, {title_color}22, {title_color}11); 
                    padding: 20px; border-radius: 15px; border-left: 5px solid {title_color}; margin-bottom: 20px;'>
            <h3 style='color: {title_color}; margin: 0;'>{emoji} Météo à {city_name}</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Météo actuelle
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🌡️ Température", f"{main.get('temp', '--')}°C")
        st.caption(f"Ressenti: {main.get('feels_like', '--')}°C")
    
    with col2:
        icon_url = get_weather_icon_url(weather.get('icon', '01d'))
        st.image(icon_url, width=80)
        st.caption(f"_{weather.get('description', 'N/A').capitalize()}_")
    
    with col3:
        st.metric("💧 Humidité", f"{main.get('humidity', '--')}%")
        st.metric("👁️ Visibilité", f"{current.get('visibility', 0)//1000} km")
    
    with col4:
        st.metric("💨 Vent", f"{wind.get('speed', '--')} m/s")
        st.metric("☁️ Nuages", f"{current.get('clouds', {}).get('all', '--')}%")
    
    # Prévisions sur 5 jours
    st.markdown("**📅 Prévisions sur 5 jours**")
    forecast_list = weather_data.get("forecast", {}).get("list", [])[:5]
    
    if forecast_list:
        cols = st.columns(5)
        for idx, (col, forecast) in enumerate(zip(cols, forecast_list)):
            with col:
                date_txt = forecast.get("dt_txt", "")[5:10]  # MM-DD
                temp = forecast.get("main", {}).get("temp", "--")
                icon = forecast.get("weather", [{}])[0].get("icon", "01d")
                desc = forecast.get("weather", [{}])[0].get("description", "")[:15]
                
                st.markdown(f"**{date_txt}**")
                st.image(get_weather_icon_url(icon), width=50)
                st.markdown(f"**{temp}°C**")
                st.caption(f"_{desc}_")

# ==================== FONCTIONS TRAJET (OPENROUTESERVICE) ====================

def geocode_address(address):
    """Géocodage via OpenRouteService."""
    if not ORS_API_KEY:
        return None
    try:
        url = "https://api.openrouteservice.org/geocode/search"
        params = {"api_key": ORS_API_KEY, "text": address, "size": 1}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if data.get("features"):
            coords = data["features"][0]["geometry"]["coordinates"]
            return coords[1], coords[0] # lat, lon
        return None
    except:
        return None

def get_route_data(origin_lat, origin_lon, dest_lat, dest_lon, mode="driving-car"):
    """Récupère les données de trajet via OpenRouteService."""
    if not ORS_API_KEY:
        return {"error": "Clé API OpenRouteService non configurée"}
    
    try:
        url = f"https://api.openrouteservice.org/v2/directions/{mode}/geojson"
        headers = {"Authorization": ORS_API_KEY, "Content-Type": "application/json"}
        body = {"coordinates": [[origin_lon, origin_lat], [dest_lon, dest_lat]], "instructions": True, "language": "fr"}
        
        response = requests.post(url, headers=headers, json=body, timeout=10)
        data = response.json()
        
        if "error" in data:
            return {"error": f"ORS Error: {data['error'].get('message', 'Unknown error')}"}
            
        summary = data["features"][0]["properties"]["summary"]
        steps = data["features"][0]["properties"]["segments"][0]["steps"]
        geometry = data["features"][0]["geometry"]["coordinates"] # GeoJSON coordinates [[lon, lat], ...]
        
        # Inverser lat/lon pour Folium
        geometry_latlon = [[coord[1], coord[0]] for coord in geometry]
        
        # Formatage pour compatibilité avec l'affichage existant
        formatted_steps = []
        for step in steps:
            formatted_steps.append({
                "html_instructions": step.get("instruction", "Continuer"),
                "distance": {"text": f"{step['distance']:.1f} m"},
                "duration": {"text": f"{step['duration']:.1f} s"}
            })
            
        return {
            "success": True,
            "distance": f"{summary['distance']/1000:.1f} km",
            "duration": f"{summary['duration']/60:.0f} min",
            "steps": formatted_steps,
            "geometry": geometry_latlon,
            "start_address": "Départ", # ORS ne donne pas l'adresse inverse ici
            "end_address": "Arrivée"
        }
            
    except Exception as e:
        return {"error": f"Erreur de connexion: {str(e)}"}



def get_pois(lat, lon, radius=1000, limit=5):
    """Récupère les POIs (Resto, Café, Hôtel) via Overpass API."""
    try:
        overpass_url = "http://overpass-api.de/api/interpreter"
        query = f"""
        [out:json];
        (
          node["amenity"="restaurant"](around:{radius},{lat},{lon});
          node["amenity"="cafe"](around:{radius},{lat},{lon});
          node["tourism"="hotel"](around:{radius},{lat},{lon});
        );
        out body {limit};
        """
        response = requests.get(overpass_url, params={'data': query}, timeout=15)
        data = response.json()
        
        pois = []
        for element in data.get('elements', []):
            pois.append({
                "name": element.get('tags', {}).get('name', 'Sans nom'),
                "type": element.get('tags', {}).get('amenity') or element.get('tags', {}).get('tourism'),
                "lat": element['lat'],
                "lon": element['lon']
            })
        return pois
    except Exception as e:
        return []

def display_route_card(route_data, origin_city, dest_city, mode="🚗"):
    """Affiche une carte de trajet."""
    if "error" in route_data:
        st.error(route_data["error"])
        return
    
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, #27ae6022, #27ae6011); 
                    padding: 20px; border-radius: 15px; border-left: 5px solid #27ae60; margin-bottom: 20px;'>
            <h3 style='color: #27ae60; margin: 0;'>{mode} Trajet: {origin_city} → {dest_city}</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Carte Folium
    if "geometry" in route_data and "start_coords" in route_data and "end_coords" in route_data:
        m = folium.Map(location=[(route_data["start_coords"][0] + route_data["end_coords"][0])/2, 
                                 (route_data["start_coords"][1] + route_data["end_coords"][1])/2], 
                       zoom_start=10)
        
        # Trajet Bleu
        folium.PolyLine(route_data["geometry"], color="blue", weight=5, opacity=0.7).add_to(m)
        
        # Marqueurs
        folium.Marker(route_data["start_coords"], popup=f"Départ", icon=folium.Icon(color="green", icon="play")).add_to(m)
        folium.Marker(route_data["end_coords"], popup=f"Arrivée", icon=folium.Icon(color="red", icon="stop")).add_to(m)
        
        # POIs
        if "pois_start" in route_data:
            for poi in route_data["pois_start"]:
                color = "orange" if poi["type"] == "restaurant" else "blue" if poi["type"] == "hotel" else "purple"
                folium.Marker([poi["lat"], poi["lon"]], popup=f"{poi['name']} ({poi['type']})", icon=folium.Icon(color=color, icon="info-sign", prefix='fa')).add_to(m)
        
        if "pois_end" in route_data:
            for poi in route_data["pois_end"]:
                color = "orange" if poi["type"] == "restaurant" else "blue" if poi["type"] == "hotel" else "purple"
                folium.Marker([poi["lat"], poi["lon"]], popup=f"{poi['name']} ({poi['type']})", icon=folium.Icon(color=color, icon="info-sign", prefix='fa')).add_to(m)

        # Utiliser use_container_width pour le mobile
        st_folium(m, height=400, use_container_width=True)
    
    # Statistiques
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📏 Distance", route_data.get("distance", "N/A"))
    with col2:
        st.metric("⏱️ Durée estimée", route_data.get("duration", "N/A"))
    with col3:
        st.metric("🛣️ Étapes", f"{len(route_data.get('steps', []))} étapes")
    
    # Adresses
    st.markdown(f"**📍 Départ:** {route_data.get('start_address', origin_city)}")
    st.markdown(f"**🏁 Arrivée:** {route_data.get('end_address', dest_city)}")
    
    # Étapes détaillées
    with st.expander("🗺️ Voir les étapes détaillées"):
        for idx, step in enumerate(route_data.get("steps", [])[:10], 1):
            instruction = step.get("html_instructions", "Continuer")
            # Nettoyer les balises HTML
            instruction = instruction.replace("<b>", "**").replace("</b>", "**")
            instruction = instruction.replace("<div>", " ").replace("</div>", "")
            instruction = instruction.replace("<wbr/>", "")
            
            step_dist = step.get("distance", {}).get("text", "0 km")
            step_dur = step.get("duration", {}).get("text", "0 min")
            
            st.markdown(f"**{idx}.** {instruction} _({step_dist} - {step_dur})_")



# ==================== FONCTIONS VOL ====================

def search_flights_api(origin_code, dest_code, travel_date, passengers=1):
    """Recherche de vols Amadeus."""
    if not amadeus:
        return {"error": "Client Amadeus non initialisé"}
    
    try:
        date_str = travel_date.strftime("%Y-%m-%d") if isinstance(travel_date, date) else str(travel_date)
        
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin_code,
            destinationLocationCode=dest_code,
            departureDate=date_str,
            adults=int(passengers),
            max=20,
            currencyCode="MAD"
        )
        
        return {"success": True, "data": response.data}
        
    except ResponseError as error:
        error_msg = f"Erreur Amadeus [{error.code}]"
        try:
            if hasattr(error, 'response') and error.response:
                error_detail = error.response.result.get('errors', [{}])[0].get('detail', '')
                if error_detail:
                    error_msg += f" - {error_detail}"
        except:
            pass
        return {"error": error_msg}
    except Exception as e:
        return {"error": f"Erreur: {str(e)}"}

def format_duration(iso_duration):
    """Formate la durée ISO."""
    duration = iso_duration.replace("PT", "")
    hours, minutes = 0, 0
    
    if "H" in duration:
        parts = duration.split("H")
        hours = int(parts[0])
        duration = parts[1] if len(parts) > 1 else ""
    
    if "M" in duration:
        minutes = int(duration.replace("M", ""))
    
    if hours > 0 and minutes > 0:
        return f"{hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h"
    else:
        return f"{minutes}m"

def display_flight_results(flights):
    """Affiche les résultats de vols."""
    if not flights:
        st.warning("Aucun vol trouvé.")
        return
    
    st.success(f"✅ {len(flights)} vol(s) trouvé(s)")
    
    for flight in flights[:10]:
        itineraries = flight.get('itineraries', [])
        price = flight.get('price', {})
        
        if not itineraries:
            continue
            
        first_itinerary = itineraries[0]
        segments = first_itinerary.get('segments', [])
        
        if not segments:
            continue
        
        first_segment = segments[0]
        last_segment = segments[-1]
        
        departure = first_segment.get('departure', {})
        arrival = last_segment.get('arrival', {})
        carrier = first_segment.get('carrierCode', 'N/A')
        
        total_price = price.get('total', 'N/A')
        currency = price.get('currency', 'MAD')
        
        with st.container():
            cols = st.columns([2, 2, 2, 1])
            
            with cols[0]:
                st.markdown(f"**🛫 {departure.get('iataCode', '?')}**")
                st.markdown(f"{departure.get('at', '?')[11:16]}")
            
            with cols[1]:
                st.markdown(f"**🛬 {arrival.get('iataCode', '?')}**")
                st.markdown(f"{arrival.get('at', '?')[11:16]}")
            
            with cols[2]:
                st.markdown(f"**✈️ {carrier}**")
                duration = first_itinerary.get('duration', '')
                if duration:
                    st.markdown(f"⏱️ {format_duration(duration)}")
                st.markdown(f"{'🔵 Direct' if len(segments) == 1 else f'🔄 {len(segments)-1} escale(s)'}")
            
            with cols[3]:
                st.markdown(f"**💰 {total_price} {currency}**")
            
            with st.expander("Détails"):
                st.json(flight)
            
            st.divider()



# ==================== INTERFACE PRINCIPALE ====================

st.title("🧳 Concierge Voyage Direct")
st.caption("✈️ Vols • 🌤️ Météo • 🗺️ Trajets - Tout-en-un!")

# Initialisation session state
for key in ['origin_search', 'dest_search', 'origin_selected', 'dest_selected', 'last_search']:
    if key not in st.session_state:
        st.session_state[key] = "" if 'search' in key or 'selected' in key else None



tab_vols, tab_meteo, tab_trajet = st.tabs(["✈️ Recherche de Vols", "🌤️ Météo & Infos", "🗺️ Trajets & Maps"])

# ==================== ONGLET VOLS ====================
with tab_vols:
    st.header("Rechercher un vol")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🛫 Départ**")
        origin_input = st.text_input(
            "Rechercher",
            value=st.session_state.origin_search,
            placeholder="Ex: rabat, RBA...",
            key="origin_input",
            label_visibility="collapsed"
        )
        
        origin_suggestions = get_airport_suggestions(origin_input)
        
        if origin_input and len(origin_input) >= 1:
            st.caption("💡 Cliquez pour sélectionner:")
            for airport in origin_suggestions[:5]:
                if st.button(
                    f"✈️ {airport['code']} - {airport['city']}, {airport['country']}", 
                    key=f"origin_{airport['code']}",
                    use_container_width=True
                ):
                    st.session_state.origin_search = airport['code']
                    st.session_state.origin_selected = format_airport_option(airport)
                    st.rerun()
        
        if st.session_state.origin_selected:
            st.success(f"✅ {st.session_state.origin_selected}")
    
    with col2:
        st.markdown("**🛬 Destination**")
        dest_input = st.text_input(
            "Rechercher",
            value=st.session_state.dest_search,
            placeholder="Ex: fes, FEZ...",
            key="dest_input",
            label_visibility="collapsed"
        )
        
        dest_suggestions = get_airport_suggestions(dest_input)
        
        if dest_input and len(dest_input) >= 1:
            st.caption("💡 Cliquez pour sélectionner:")
            for airport in dest_suggestions[:5]:
                if st.button(
                    f"✈️ {airport['code']} - {airport['city']}, {airport['country']}", 
                    key=f"dest_{airport['code']}",
                    use_container_width=True
                ):
                    st.session_state.dest_search = airport['code']
                    st.session_state.dest_selected = format_airport_option(airport)
                    st.rerun()
        
        if st.session_state.dest_selected:
            st.success(f"✅ {st.session_state.dest_selected}")
    
    with col3:
        st.markdown("**📅 Date & Passagers**")
        travel_date = st.date_input("Date", value=date.today(), min_value=date.today(), label_visibility="collapsed")
        passengers = st.number_input("Passagers", min_value=1, max_value=9, value=1, label_visibility="collapsed")
    
    # Bouton recherche
    if st.button("🔍 Rechercher les Vols", type="primary", use_container_width=True):
        origin_code = get_iata_code_from_selection(st.session_state.origin_selected)
        dest_code = get_iata_code_from_selection(st.session_state.dest_selected)
        
        if not origin_code or not dest_code:
            st.error("❌ Veuillez sélectionner les aéroports de départ et destination")
        elif origin_code == dest_code:
            st.error("❌ Le départ et la destination doivent être différents")
        else:
            # Sauvegarder pour les autres onglets
            st.session_state.last_search = {
                "origin": origin_code,
                "destination": dest_code,
                "origin_airport": get_airport_by_code(origin_code),
                "dest_airport": get_airport_by_code(dest_code)
            }
            
            with st.spinner("Recherche en cours..."):
                result = search_flights_api(origin_code, dest_code, travel_date, passengers)
                
                if "error" in result:
                    st.error(f"❌ {result['error']}")
                else:
                    display_flight_results(result.get('data', []))

# ==================== ONGLET MÉTÉO ====================
with tab_meteo:
    st.header("🌤️ Météo des Aéroports")
    
    # Utiliser la dernière recherche ou permettre sélection manuelle
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🛫 Aéroport de Départ")
        origin_ap = None
        if st.session_state.last_search and st.session_state.last_search.get("origin_airport"):
            origin_ap = st.session_state.last_search["origin_airport"]
            st.info(f"Utilisé depuis la recherche: **{origin_ap['city']} ({origin_ap['code']})**")
            weather_origin = get_weather_data(origin_ap["lat"], origin_ap["lon"], origin_ap["city"])
            display_weather_card(weather_origin, origin_ap["city"], is_destination=False)
        else:
            # Sélection manuelle
            weather_origin_input = st.text_input("Rechercher ville de départ", key="weather_origin", placeholder="Ex: rabat")
            if weather_origin_input:
                suggestions = get_airport_suggestions(weather_origin_input)
                if suggestions:
                    origin_ap = suggestions[0]
                    if st.button(f"Voir météo pour {origin_ap['city']}", key="btn_weather_origin"):
                        weather_data = get_weather_data(origin_ap["lat"], origin_ap["lon"], origin_ap["city"])
                        display_weather_card(weather_data, origin_ap["city"], is_destination=False)
        
        # Affichage des POIs Départ


    with col2:
        st.subheader("🛬 Aéroport de Destination")
        dest_ap = None
        if st.session_state.last_search and st.session_state.last_search.get("dest_airport"):
            dest_ap = st.session_state.last_search["dest_airport"]
            st.info(f"Utilisé depuis la recherche: **{dest_ap['city']} ({dest_ap['code']})**")
            weather_dest = get_weather_data(dest_ap["lat"], dest_ap["lon"], dest_ap["city"])
            display_weather_card(weather_dest, dest_ap["city"], is_destination=True)
        else:
            # Sélection manuelle
            weather_dest_input = st.text_input("Rechercher ville de destination", key="weather_dest", placeholder="Ex: fes")
            if weather_dest_input:
                suggestions = get_airport_suggestions(weather_dest_input)
                if suggestions:
                    dest_ap = suggestions[0]
                    if st.button(f"Voir météo pour {dest_ap['city']}", key="btn_weather_dest"):
                        weather_data = get_weather_data(dest_ap["lat"], dest_ap["lon"], dest_ap["city"])
                        display_weather_card(weather_data, dest_ap["city"], is_destination=True)
        
        # Affichage des POIs Arrivée


# ==================== ONGLET TRAJET ====================
with tab_trajet:
    st.header("🗺️ Trajets & Navigation")
    
    # Mode: Depuis l'aéroport OU Vers l'aéroport
    trajet_mode = st.radio(
        "Type de trajet",
        ["🚗 Depuis l'aéroport (vers centre-ville)", "🚗 Vers l'aéroport (depuis centre-ville)", "🗺️ Trajet personnalisé"],
        horizontal=True
    )
    
    if trajet_mode == "🗺️ Trajet personnalisé":
        # Trajet libre
        col1, col2 = st.columns(2)
        with col1:
            origin_address = st.text_input("📍 Adresse de départ", placeholder="Ex: Gare Rabat Ville, Maroc")
        with col2:
            dest_address = st.text_input("🏁 Adresse d'arrivée", placeholder="Ex: Aéroport Rabat-Salé, Maroc")
        
        if st.button("Calculer le trajet", type="primary"):
            if origin_address and dest_address:
                with st.spinner("Calcul de l'itinéraire..."):
                    # 1. Géocodage
                    origin_coords = geocode_address(origin_address)
                    dest_coords = geocode_address(dest_address)
                    
                    if not origin_coords or not dest_coords:
                        st.error("❌ Adresse introuvable via OpenRouteService")
                    else:
                        # 2. Calcul itinéraire
                        route_data = get_route_data(
                            origin_coords[0], origin_coords[1],
                            dest_coords[0], dest_coords[1]
                        )
                        
                        # Ajout coordonnées pour la carte
                        route_data["start_coords"] = origin_coords
                        route_data["end_coords"] = dest_coords
                        
                        # POIs
                        route_data["pois_start"] = get_pois(origin_coords[0], origin_coords[1])
                        route_data["pois_end"] = get_pois(dest_coords[0], dest_coords[1])
                        
                        if "error" in route_data:
                            st.error(f"❌ {route_data['error']}")
                        else:
                            # 3. Affichage
                            display_route_card(route_data, origin_address, dest_address)
                            
                            # Lien externe
                            osm_url = f"https://www.openstreetmap.org/directions?engine=graphhopper_car&route={origin_coords[0]}%2C{origin_coords[1]}%3B{dest_coords[0]}%2C{dest_coords[1]}"
                            st.markdown(f"**[🗺️ Voir sur OpenStreetMap]({osm_url})**")
            else:
                st.warning("Veuillez entrer les deux adresses")
    
    else:
        # Trajet depuis/vers aéroport avec données de la recherche
        if st.session_state.last_search:
            origin_ap = st.session_state.last_search.get("origin_airport")
            dest_ap = st.session_state.last_search.get("dest_airport")
            
            if trajet_mode.startswith("🚗 Depuis"):
                # Trajet depuis aéroport de départ vers centre-ville
                if origin_ap:
                    st.subheader(f"🚗 De {origin_ap['name']} vers le centre de {origin_ap['city']}")
                    
                    # Coordonnées approximatives du centre-ville (à ajuster selon la ville)
                    city_centers = {
                        "Rabat": (34.0209, -6.8416),
                        "Casablanca": (33.5731, -7.5898),
                        "Marrakech": (31.6295, -7.9811),
                        "Fès": (34.0181, -5.0078),
                        "Tanger": (35.7595, -5.8340),
                        "Agadir": (30.4278, -9.5981),
                    }
                    
                    center = city_centers.get(origin_ap["city"], (origin_ap["lat"] + 0.05, origin_ap["lon"] + 0.05))
                    
                    width = 450
                    
                    # Calcul itinéraire réel
                    with st.spinner("Calcul de l'itinéraire..."):
                        route_data = get_route_data(
                            origin_ap["lat"], origin_ap["lon"],
                            center[0], center[1]
                        )
                        
                        route_data["start_coords"] = (origin_ap["lat"], origin_ap["lon"])
                        route_data["end_coords"] = center
                        route_data["pois_start"] = get_pois(origin_ap["lat"], origin_ap["lon"])
                        route_data["pois_end"] = get_pois(center[0], center[1])
                        
                        if "error" in route_data:
                            st.error(f"Erreur itinéraire: {route_data['error']}")
                        else:
                            display_route_card(route_data, origin_ap["name"], f"Centre {origin_ap['city']}")
                            
                            # Lien externe
                            osm_url = f"https://www.openstreetmap.org/directions?engine=graphhopper_car&route={origin_ap['lat']}%2C{origin_ap['lon']}%3B{center[0]}%2C{center[1]}"
                            st.markdown(f"**[🗺️ Voir sur OpenStreetMap]({osm_url})**")
                    
                    # Options de transport
                    st.markdown("### 🚕 Options de transport")
                    transport_cols = st.columns(3)
                    with transport_cols[0]:
                        st.markdown("""
                            <div style='text-align: center; padding: 15px; background: #e8f5e9; border-radius: 10px;'>
                                <h4>🚕 Taxi</h4>
                                <p>~100 MAD</p>
                                <small>Disponible 24/7</small>
                            </div>
                        """, unsafe_allow_html=True)
                    with transport_cols[1]:
                        st.markdown("""
                            <div style='text-align: center; padding: 15px; background: #e3f2fd; border-radius: 10px;'>
                                <h4>🚗 Uber/Careem</h4>
                                <p>~80-120 MAD</p>
                                <small>Via application</small>
                            </div>
                        """, unsafe_allow_html=True)
                    with transport_cols[2]:
                        st.markdown("""
                            <div style='text-align: center; padding: 15px; background: #fff3e0; border-radius: 10px;'>
                                <h4>🚌 Bus</h4>
                                <p>~20-30 MAD</p>
                                <small>Airport Express</small>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    # Points d'intérêt
                    with st.expander("🏛️ Points d'intérêt à proximité"):
                        pois = {
                            "Rabat": ["Tour Hassan", "Kasbah des Oudayas", "Médina de Rabat", "Plage des Nations"],
                            "Casablanca": ["Mosquée Hassan II", "Corniche", "Quartier Habous", "Marché Central"],
                            "Marrakech": ["Jemaa el-Fna", "Jardins Majorelle", "Médina", "Palais Bahia"],
                            "Fès": ["Médina de Fès", "Al-Qarawiyyin", "Tanneries de Chouara", "Bab Bou Jeloud"],
                        }
                        city_pois = pois.get(origin_ap["city"], ["Centre-ville", "Gare", "Médina"])
                        for poi in city_pois:
                            st.markdown(f"• {poi}")
            
            else:
                # Trajet vers aéroport de destination
                if dest_ap:
                    st.subheader(f"🚗 Du centre de {dest_ap['city']} vers {dest_ap['name']}")
                    
                    city_centers = {
                        "Rabat": (34.0209, -6.8416),
                        "Casablanca": (33.5731, -7.5898),
                        "Marrakech": (31.6295, -7.9811),
                        "Fès": (34.0181, -5.0078),
                        "Tanger": (35.7595, -5.8340),
                        "Agadir": (30.4278, -9.5981),
                    }
                    
                    center = city_centers.get(dest_ap["city"], (dest_ap["lat"] + 0.05, dest_ap["lon"] + 0.05))
                    
                    width = 450
                    
                    # Calcul itinéraire réel
                    with st.spinner("Calcul de l'itinéraire..."):
                        route_data = get_route_data(
                            center[0], center[1],
                            dest_ap["lat"], dest_ap["lon"]
                        )
                        
                        route_data["start_coords"] = center
                        route_data["end_coords"] = (dest_ap["lat"], dest_ap["lon"])
                        route_data["pois_start"] = get_pois(center[0], center[1])
                        route_data["pois_end"] = get_pois(dest_ap["lat"], dest_ap["lon"])
                        
                        if "error" in route_data:
                            st.error(f"Erreur itinéraire: {route_data['error']}")
                        else:
                            display_route_card(route_data, f"Centre {dest_ap['city']}", dest_ap["name"])
                            
                            # Lien externe
                            osm_url = f"https://www.openstreetmap.org/directions?engine=graphhopper_car&route={center[0]}%2C{center[1]}%3B{dest_ap['lat']}%2C{dest_ap['lon']}"
                            st.markdown(f"**[🗺️ Voir sur OpenStreetMap]({osm_url})**")
                    
                    # Alertes spéciales aéroport
                    st.markdown("### ⚠️ Infos Aéroport")
                    st.info(f"""
                        **{dest_ap['name']} ({dest_ap['code']})**
                        - 📍 Localisation: {dest_ap['city']}, {dest_ap['country']}
                        - ⏰ Conseil: Arrivez 2h avant pour les vols internationaux
                        - 🅿️ Parking disponible
                        - ☕ Restaurants et boutiques duty-free
                    """)
        else:
            st.info("💡 Effectuez d'abord une recherche de vol dans l'onglet '✈️ Recherche de Vols' pour voir les trajets automatiques, ou utilisez le mode 'Trajet personnalisé' ci-dessus.")

# ==================== SIDEBAR ====================
with st.sidebar:
    st.title("⚙️ Configuration")
    
    # Statut des APIs
    st.subheader("🔌 Statut des Services")
    
    if amadeus:
        st.success("✅ Amadeus API")
    else:
        st.error("❌ Amadeus API")
    
    if OPENWEATHER_API_KEY:
        st.success("✅ OpenWeather")
    else:
        st.warning("⚠️ OpenWeather (clé manquante)")
    
    if ORS_API_KEY:
        st.success("✅ OpenRouteService")
    else:
        st.warning("⚠️ OpenRouteService (clé manquante)")
    
    st.markdown("---")
    
    # Configuration rapide
    with st.expander("🔧 Configuration API"):
        st.markdown("""
            Créez un fichier `.streamlit/secrets.toml`:
            ```toml
            AMADEUS_API_KEY = "votre_cle"
            AMADEUS_API_SECRET = "votre_secret"
            OPENWEATHER_API_KEY = "votre_cle_openweather"
            ORS_API_KEY = "votre_cle_ors"
            ```
        """)
    
    st.markdown("---")
    
    # Réinitialisation
    if st.button("🔄 Réinitialiser tout", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Footer
st.markdown("---")
st.caption("🔒 Données: Amadeus | OpenWeather | OpenRouteService | Application Streamlit locale")