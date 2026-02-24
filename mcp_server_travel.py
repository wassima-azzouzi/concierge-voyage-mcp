"""
Serveur MCP - Concierge Voyage
Outils: Amadeus (Vols), OpenWeather (Météo), ORS (Routes)
"""

import os
import json
import sys
import requests
from datetime import datetime
from typing import Optional, List, Dict
from fastmcp import FastMCP
from amadeus import Client, ResponseError
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("ConciergeVoyage")

# Configuration API
amadeus = Client(
    client_id=os.getenv("AMADEUS_API_KEY"),
    client_secret=os.getenv("AMADEUS_API_SECRET")
)
OPENWEATHER_KEY = os.getenv("OPENWEATHER_API_KEY")
ORS_KEY = os.getenv("ORS_API_KEY")


@mcp.tool()
def search_flights(origin: str, destination: str, date: str, adults: int = 1) -> str:
    """
    Recherche de vols via Amadeus (vraies données temps réel)
    """
    try:
        # Conversion villes → codes IATA
        origin_code = _get_iata_code(origin)
        dest_code = _get_iata_code(destination)
        
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin_code,
            destinationLocationCode=dest_code,
            departureDate=date,
            adults=adults,
            max=3,
            currencyCode="EUR"
        )
        
        flights = []
        for offer in response.data:
            price = offer['price']['total']
            itinerary = offer['itineraries'][0]
            segment = itinerary['segments'][0]
            
            flights.append({
                "prix": f"{price} EUR",
                "compagnie": segment['carrierCode'],
                "numero_vol": f"{segment['carrierCode']}{segment['number']}",
                "depart": segment['departure']['at'],
                "arrivee": segment['arrival']['at'],
                "duree": itinerary['duration'].replace('PT', '').lower(),
                "escales": len(itinerary['segments']) - 1
            })
        
        return json.dumps({
            "status": "success",
            "origine": origin_code,
            "destination": dest_code,
            "date": date,
            "offres": flights,
            "source": "Amadeus (Données temps réel)"
        }, ensure_ascii=False, indent=2)
        
    except ResponseError as e:
        return json.dumps({
            "status": "error",
            "message": f"Erreur Amadeus: {str(e)}",
            "conseil": "Vérifiez les codes IATA (PAR, ROM, NYC...)"
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        }, ensure_ascii=False)


@mcp.tool()
def get_weather_forecast(city: str, date: str) -> str:
    """
    Météo via OpenWeather (votre clé)
    """
    try:
        url = "http://api.openweathermap.org/data/2.5/forecast"
        params = {
            "q": city,
            "appid": OPENWEATHER_KEY,
            "units": "metric",
            "lang": "fr"
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if response.status_code != 200:
            # Fallback Open-Meteo
            return _fallback_weather(city, date)
        
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
        forecasts = []
        
        for item in data['list']:
            forecast_time = datetime.fromtimestamp(item['dt'])
            if forecast_time.date() == target_date:
                forecasts.append({
                    "heure": forecast_time.strftime("%H:%M"),
                    "temp": round(item['main']['temp']),
                    "description": item['weather'][0]['description'],
                    "humidite": item['main']['humidity'],
                    "vent": item['wind']['speed']
                })
        
        if not forecasts:
            return _fallback_weather(city, date)
        
        temps = [f['temp'] for f in forecasts]
        descriptions = [f['description'] for f in forecasts]
        
        return json.dumps({
            "status": "success",
            "ville": city,
            "date": date,
            "temp_min": min(temps),
            "temp_max": max(temps),
            "condition": max(set(descriptions), key=descriptions.count),
            "previsions": forecasts[:4],
            "source": "OpenWeather"
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return _fallback_weather(city, date)


def _fallback_weather(city: str, date: str) -> str:
    """Fallback gratuit sans clé"""
    try:
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo = requests.get(geo_url, params={"name": city, "count": 1}, timeout=10).json()
        
        if not geo.get("results"):
            return json.dumps({"status": "error", "message": "Ville non trouvée"}, ensure_ascii=False)
        
        lat, lon = geo["results"][0]["latitude"], geo["results"][0]["longitude"]
        
        weather_url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat, "longitude": lon,
            "daily": ["temperature_2m_max", "temperature_2m_min", "weathercode"],
            "timezone": "auto", "forecast_days": 16
        }
        
        data = requests.get(weather_url, params=params, timeout=10).json()
        target = datetime.strptime(date, "%Y-%m-%d").date()
        today = datetime.now().date()
        idx = (target - today).days
        
        if idx < 0 or idx >= len(data["daily"]["time"]):
            return json.dumps({"status": "error", "message": "Date hors limites"}, ensure_ascii=False)
        
        codes = {0: "Ensoleillé", 1: "Ensoleillé", 2: "Nuageux", 3: "Nuageux", 
                61: "Pluie", 63: "Pluie", 95: "Orage"}
        
        return json.dumps({
            "status": "success",
            "ville": city,
            "date": date,
            "temp_max": round(data["daily"]["temperature_2m_max"][idx]),
            "temp_min": round(data["daily"]["temperature_2m_min"][idx]),
            "condition": codes.get(data["daily"]["weathercode"][idx], "Variable"),
            "source": "Open-Meteo (Fallback gratuit)"
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)


@mcp.tool()
def get_travel_time(origin: str, destination: str, mode: str = "driving-car") -> str:
    """
    Routes via OpenRouteService (votre clé)
    """
    try:
        # Géocodage
        def geocode(address):
            url = "https://api.openrouteservice.org/geocode/search"
            params = {"api_key": ORS_KEY, "text": address, "size": 1}
            r = requests.get(url, params=params, timeout=10).json()
            return r["features"][0]["geometry"]["coordinates"] if r["features"] else None
        
        coords_orig = geocode(origin)
        coords_dest = geocode(destination)
        
        if not coords_orig or not coords_dest:
            return _fallback_route(origin, destination, mode)
        
        # Calcul route
        url = f"https://api.openrouteservice.org/v2/directions/{mode}"
        headers = {"Authorization": ORS_KEY, "Content-Type": "application/json"}
        body = {"coordinates": [coords_orig, coords_dest], "instructions": False}
        
        r = requests.post(url, headers=headers, json=body, timeout=10).json()
        
        if "error" in r:
            return _fallback_route(origin, destination, mode)
        
        summary = r["routes"][0]["summary"]
        
        return json.dumps({
            "status": "success",
            "origine": origin,
            "destination": destination,
            "mode": _translate_mode(mode),
            "distance_km": round(summary["distance"] / 1000, 2),
            "duree": _format_duration(summary["duration"]),
            "source": "OpenRouteService"
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return _fallback_route(origin, destination, mode)


def _fallback_route(origin: str, destination: str, mode: str) -> str:
    """Fallback OSRM sans clé"""
    try:
        osrm_mode = "car" if "driving" in mode else "foot" if "foot" in mode else "bike"
        
        def geocode(address):
            url = "https://nominatim.openstreetmap.org/search"
            headers = {"User-Agent": "ConciergeVoyage/1.0"}
            params = {"q": address, "format": "json", "limit": 1}
            r = requests.get(url, params=params, headers=headers, timeout=10).json()
            return (float(r[0]["lon"]), float(r[0]["lat"])) if r else None
        
        c1, c2 = geocode(origin), geocode(destination)
        if not c1 or not c2:
            return json.dumps({"status": "error", "message": "Adresse non trouvée"}, ensure_ascii=False)
        
        url = f"http://router.project-osrm.org/route/v1/{osrm_mode}/{c1[0]},{c1[1]};{c2[0]},{c2[1]}"
        r = requests.get(url, params={"overview": "false"}, timeout=10).json()
        
        if r.get("code") != "Ok":
            return json.dumps({"status": "error", "message": "Route impossible"}, ensure_ascii=False)
        
        route = r["routes"][0]
        
        return json.dumps({
            "status": "success",
            "origine": origin,
            "destination": destination,
            "mode": _translate_mode(mode),
            "distance_km": round(route["distance"] / 1000, 1),
            "duree": _format_duration(route["duration"]),
            "source": "OSRM (Fallback gratuit)"
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)


def _get_iata_code(city: str) -> str:
    codes = {
        "paris": "PAR", "londres": "LON", "london": "LON",
        "rome": "ROM", "milan": "MIL", "barcelone": "BCN",
        "barcelona": "BCN", "madrid": "MAD", "amsterdam": "AMS",
        "berlin": "BER", "new york": "NYC", "los angeles": "LAX",
        "tokyo": "TYO", "dubai": "DXB", "singapour": "SIN",
        "lyon": "LYS", "marseille": "MRS", "nice": "NCE",
        "toulouse": "TLS", "bordeaux": "BOD", "nantes": "NTE",
        "strasbourg": "SXB", "bruxelles": "BRU", "geneve": "GVA"
    }
    return codes.get(city.lower(), city.upper())


def _translate_mode(mode: str) -> str:
    modes = {
        "driving-car": "Voiture",
        "cycling-regular": "Vélo",
        "foot-walking": "Marche",
        "wheelchair": "Fauteuil roulant"
    }
    return modes.get(mode, mode)


def _format_duration(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    return f"{h}h {m}min" if h > 0 else f"{m} min"


# Mode CLI pour app_standalone.py
if __name__ == "__main__":
    if len(sys.argv) > 2:
        # Mode CLI
        tool_name = sys.argv[1]
        param_file = sys.argv[2]
        
        with open(param_file) as f:
            params = json.load(f)
        
        if tool_name == "search_flights":
            print(search_flights(**params))
        elif tool_name == "get_weather_forecast":
            print(get_weather_forecast(**params))
        elif tool_name == "get_travel_time":
            print(get_travel_time(**params))
    else:
        # Mode MCP standard
        mcp.run(transport='stdio')