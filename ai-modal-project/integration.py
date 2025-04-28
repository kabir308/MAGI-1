"""
Module d'intégration pour le AI Modal dans le projet MAGI-1.
Ce module fournit des fonctions utilitaires pour lancer et interagir avec l'API IA.
"""

import os
import sys
import subprocess
import threading
import time
import requests
from pathlib import Path


class AIModalIntegration:
    def __init__(self, backend_path=None, frontend_path=None):
        """
        Initialise l'intégration du modal IA.
        
        Args:
            backend_path: Chemin vers le dossier backend (par défaut: detecté automatiquement)
            frontend_path: Chemin vers le dossier frontend (par défaut: detecté automatiquement)
        """
        # Détecte les chemins automatiquement si non spécifiés
        current_dir = Path(__file__).parent
        self.backend_path = backend_path or (current_dir / "backend").resolve()
        self.frontend_path = frontend_path or (current_dir / "frontend").resolve()
        
        # États des serveurs
        self.backend_process = None
        self.frontend_process = None
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
    
    def start_backend(self, port=8000):
        """Lance le serveur backend FastAPI."""
        if self.backend_process:
            print("Le backend est déjà en cours d'exécution.")
            return
        
        os.chdir(self.backend_path)
        cmd = [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", str(port)]
        
        self.backend_process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Attend que le serveur soit prêt
        time.sleep(2)
        print(f"Backend lancé à l'adresse: {self.backend_url}")
    
    def start_frontend(self, port=3000):
        """Lance le serveur frontend React."""
        if self.frontend_process:
            print("Le frontend est déjà en cours d'exécution.")
            return
        
        os.chdir(self.frontend_path)
        
        # Sur Windows
        if os.name == 'nt':
            cmd = ["npm.cmd", "start"]
        else:
            cmd = ["npm", "start"]
        
        # Définir la variable d'environnement PORT pour React
        env = os.environ.copy()
        env["PORT"] = str(port)
        
        self.frontend_process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Attend que le serveur soit prêt
        time.sleep(5)
        print(f"Frontend lancé à l'adresse: {self.frontend_url}")
    
    def stop_servers(self):
        """Arrête les serveurs backend et frontend."""
        if self.backend_process:
            self.backend_process.terminate()
            self.backend_process = None
            print("Backend arrêté.")
        
        if self.frontend_process:
            self.frontend_process.terminate()
            self.frontend_process = None
            print("Frontend arrêté.")
    
    def send_ai_request(self, prompt, max_tokens=150):
        """
        Envoie une requête directement à l'API IA sans passer par le frontend.
        
        Args:
            prompt: La question ou instruction pour l'IA
            max_tokens: Nombre maximum de tokens pour la réponse
            
        Returns:
            Le texte de la réponse de l'IA
        """
        try:
            response = requests.post(
                f"{self.backend_url}/api/process",
                json={"prompt": prompt, "max_tokens": max_tokens}
            )
            
            if response.status_code == 200:
                return response.json()["result"]
            else:
                return f"Erreur {response.status_code}: {response.text}"
                
        except requests.RequestException as e:
            return f"Erreur de connexion: {str(e)}"
    
    def start_all(self):
        """Lance à la fois le backend et le frontend."""
        # Lancer le backend dans un thread
        backend_thread = threading.Thread(target=self.start_backend)
        backend_thread.daemon = True
        backend_thread.start()
        
        # Lancer le frontend dans un thread
        frontend_thread = threading.Thread(target=self.start_frontend)
        frontend_thread.daemon = True
        frontend_thread.start()
        
        print("Services IA Modal démarrés. Appuyez sur Ctrl+C pour arrêter.")
        
        try:
            # Garder le programme principal en vie
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_servers()
            print("Services arrêtés.")


# Exemple d'utilisation directe du module
if __name__ == "__main__":
    integration = AIModalIntegration()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "backend":
            integration.start_backend()
            input("Appuyez sur Entrée pour arrêter le serveur...")
        elif sys.argv[1] == "frontend":
            integration.start_frontend()
            input("Appuyez sur Entrée pour arrêter le serveur...")
        elif sys.argv[1] == "all":
            integration.start_all()
        elif sys.argv[1] == "query" and len(sys.argv) > 2:
            # Exemple: python integration.py query "Comment fonctionne l'IA?"
            integration.start_backend()
            time.sleep(2)  # Attendre que le backend démarre
            response = integration.send_ai_request(" ".join(sys.argv[2:]))
            print("\nRéponse de l'IA:")
            print(response)
            integration.stop_servers()
    else:
        print("""
Usage:
    python integration.py backend  # Lance uniquement le backend
    python integration.py frontend # Lance uniquement le frontend
    python integration.py all      # Lance les deux services
    python integration.py query "Votre question ici"  # Envoie une requête directe à l'API
        """)
