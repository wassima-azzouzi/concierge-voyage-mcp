"""
Lanceur universel - Détecte et corrige automatiquement les problèmes
"""

import subprocess
import sys
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    print("=" * 50)
    print(" CONCIERGE VOYAGE MCP - Lanceur")
    print("=" * 50)
    
    # Vérifier l'environnement
    print(f"\nPython: {sys.executable}")
    print(f"Version: {sys.version.split()[0]}")
    
    # Vérifier les dépendances
    print("\nVérification des dépendances...")
    
    # Mapping package -> import
    deps_map = {
        "streamlit": "streamlit",
        "mcp": "mcp",
        "fastmcp": "fastmcp",
        "requests": "requests",
        "amadeus": "amadeus",
        "google-generativeai": "google.generativeai",
        "python-dotenv": "dotenv",
        "folium": "folium",
        "streamlit-folium": "streamlit_folium"
    }
    
    missing = []
    
    for package, import_name in deps_map.items():
        try:
            __import__(import_name)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} ({import_name}) - MANQUANT")
            missing.append(package)
    
    if missing:
        print(f"\nInstallation des dépendances manquantes: {missing}")
        subprocess.run([sys.executable, "-m", "pip", "install"] + missing)
    
    print("\n" + "=" * 50)
    print("🚀 Lancement de CONCIERGE VOYAGE (Mode Direct)...")
    print("=" * 50)
    
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app_direct.py"])

if __name__ == "__main__":
    main()