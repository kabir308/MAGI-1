"""
Exemple d'intégration du module AI Modal avec le pipeline MAGI-1. 
Ce script montre comment incorporer notre modal IA dans le pipeline existant,
en utilisant plusieurs fournisseurs d'IA et en prenant en charge la visualisation vidéo.
"""

import sys
import os
import json
import argparse
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List, Union

# Ajouter le répertoire parent au PYTHONPATH pour importer les modules MAGI-1
sys.path.append(str(Path(__file__).parent.parent))

# Importer les modules MAGI-1 nécessaires
from inference.pipeline import entry
from inference.common import config, logger

# Importer notre module d'intégration AI Modal
from integration import AIModalIntegration

# Configurer le logger
log = logger.get_logger("MAGI-AI-Modal-Integration")

class MAGIAIModalPipeline:
    """Intégration du Modal IA avec le pipeline MAGI-1."""
    
    def __init__(self, config_path=None, ai_provider="openai"):
        """
        Initialise l'intégration.
        
        Args:
            config_path: Chemin vers un fichier de configuration MAGI-1 (facultatif)
            ai_provider: Fournisseur d'IA à utiliser ("openai", "anthropic", "deepseek")
        """
        # Initialiser la configuration MAGI
        self.magi_config = config.load_config(config_path) if config_path else None
        self.ai_provider = ai_provider
        
        # Initialiser l'intégration AI Modal
        self.ai_modal = AIModalIntegration()
        
        # Initialiser le pipeline MAGI (si nécessaire)
        self.magi_pipeline = None
        log.info("Intégration MAGI-AI-Modal initialisée")
    
    def start_ai_services(self, backend_only=False):
        """
        Démarre les services AI Modal nécessaires.
        
        Args:
            backend_only: Si True, démarre uniquement le backend sans interface utilisateur
        """
        if backend_only:
            self.ai_modal.start_backend()
        else:
            # Démarrer backend et frontend
            self.ai_modal.start_all()
        
        log.info("Services AI Modal démarrés")
    
    def initialize_magi_pipeline(self):
        """Initialise le pipeline MAGI pour le traitement vidéo."""
        log.info("Initialisation du pipeline MAGI...")
        self.magi_pipeline = entry.build_pipeline(self.magi_config)
        log.info("Pipeline MAGI initialisé")
    
    def upload_video_for_analysis(self, video_path):
        """
        Uploade une vidéo sur le serveur pour analyse par l'IA.
        
        Args:
            video_path: Chemin vers la vidéo à analyser
            
        Returns:
            Dict avec les informations de la vidéo uploadée
        """
        log.info(f"Upload de la vidéo pour analyse: {video_path}")
        
        if not os.path.exists(video_path):
            log.error(f"Le fichier vidéo {video_path} n'existe pas")
            return None
            
        try:
            with open(video_path, 'rb') as video_file:
                files = {'file': (os.path.basename(video_path), video_file, 'video/mp4')}
                response = requests.post(
                    'http://localhost:8000/api/upload-video',
                    files=files
                )
                
                if response.status_code == 200:
                    video_info = response.json()
                    log.info(f"Vidéo uploadée avec succès. ID: {video_info['file_id']}")
                    return video_info
                else:
                    log.error(f"Erreur lors de l'upload: {response.status_code} - {response.text}")
                    return None
        except Exception as e:
            log.error(f"Exception lors de l'upload de la vidéo: {str(e)}")
            return None
    
    def analyze_video(self, video_info, prompt, provider=None):
        """
        Analyse une vidéo avec l'IA.
        
        Args:
            video_info: Informations sur la vidéo (à partir de upload_video_for_analysis)
            prompt: Instruction pour l'IA
            provider: Fournisseur d'IA à utiliser (par défaut: celui configuré lors de l'initialisation)
            
        Returns:
            La réponse de l'IA
        """
        if not video_info or 'file_id' not in video_info:
            log.error("Informations vidéo manquantes ou incorrectes")
            return None
            
        try:
            api_provider = provider or self.ai_provider
            log.info(f"Analyse de la vidéo {video_info['file_id']} avec {api_provider}")
            
            response = requests.post(
                'http://localhost:8000/api/analyze-video',
                json={
                    "video_id": video_info["file_id"],
                    "prompt": prompt,
                    "provider": api_provider
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["result"]
            else:
                log.error(f"Erreur lors de l'analyse: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            log.error(f"Exception lors de l'analyse de la vidéo: {str(e)}")
            return None
    
    def process_with_ai_enhancement(self, input_path, output_path, ai_prompt=None, ai_provider=None):
        """
        Traite une vidéo avec MAGI et ajoute une amélioration par l'IA.
        
        Args:
            input_path: Chemin vers la vidéo d'entrée
            output_path: Chemin où enregistrer la vidéo de sortie
            ai_prompt: Instruction spécifique pour l'IA (facultatif)
            ai_provider: Fournisseur d'IA à utiliser (par défaut: celui configuré lors de l'initialisation)
            
        Returns:
            Dict avec les chemins de sortie et les informations d'analyse
        """
        if not self.magi_pipeline:
            self.initialize_magi_pipeline()
        
        # Étape 1: Traitement MAGI standard
        log.info(f"Traitement de la vidéo avec MAGI: {input_path}")
        intermediate_result = self.magi_pipeline.process(input_path)
        
        # Étape 2: Amélioration par IA si un prompt est fourni
        ai_output_path = None
        video_info = None
        ai_response = None
        
        if ai_prompt:
            log.info("Application de l'amélioration IA...")
            
            # D'abord enregistrer la vidéo intermédiaire temporairement
            temp_video_path = output_path.replace('.mp4', '_temp.mp4')
            with open(temp_video_path, 'wb') as f:
                f.write(intermediate_result)
            
            # Uploader la vidéo pour analyse
            video_info = self.upload_video_for_analysis(temp_video_path)
            
            if video_info:
                # Analyser la vidéo avec l'IA
                provider = ai_provider or self.ai_provider
                ai_response = self.analyze_video(video_info, ai_prompt, provider)
                
                if ai_response:
                    # Enregistrer la réponse de l'IA dans un fichier à côté de la vidéo
                    ai_output_path = output_path.replace('.mp4', f'_ai_analysis_{provider}.txt') 
                    with open(ai_output_path, 'w', encoding='utf-8') as f:
                        f.write(ai_response)
                    
                    log.info(f"Analyse IA ({provider}) enregistrée dans: {ai_output_path}")
            
            # Supprimer le fichier temporaire
            try:
                os.remove(temp_video_path)
            except Exception as e:
                log.warning(f"Impossible de supprimer le fichier temporaire: {str(e)}")
        
        # Étape 3: Finalisation et enregistrement
        log.info(f"Enregistrement du résultat final dans: {output_path}")
        # Ici, simulons l'enregistrement final (à adapter selon votre pipeline réel)
        with open(output_path, 'wb') as f:
            f.write(intermediate_result)
        
        return {
            "output_video": output_path,
            "ai_analysis": ai_output_path,
            "ai_response": ai_response,
            "video_info": video_info,
            "ai_provider": ai_provider or self.ai_provider
        }
    
    def close(self):
        """Nettoie les ressources et arrête les services."""
        self.ai_modal.stop_servers()
        log.info("Services AI Modal arrêtés")


# Exemple d'utilisation
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Intégration MAGI-AI-Modal")
    parser.add_argument("--input", "-i", required=True, help="Chemin vers la vidéo d'entrée")
    parser.add_argument("--output", "-o", required=True, help="Chemin où enregistrer la vidéo de sortie")
    parser.add_argument("--prompt", "-p", help="Instructions pour l'IA concernant la vidéo")
    parser.add_argument("--provider", "-a", choices=["openai", "anthropic", "deepseek"], 
                       default="openai", help="Fournisseur d'IA à utiliser")
    parser.add_argument("--config", "-c", help="Chemin vers un fichier de configuration MAGI")
    parser.add_argument("--ui", action="store_true", help="Démarrer l'interface utilisateur au lieu du traitement par lot")
    
    args = parser.parse_args()
    
    # Initialiser l'intégration
    pipeline = MAGIAIModalPipeline(config_path=args.config, ai_provider=args.provider)
    
    try:
        if args.ui:
            # Démarrer le frontend et le backend pour une utilisation interactive
            print(f"Démarrage de l'interface utilisateur IA Modal avec le fournisseur {args.provider}...")
            pipeline.start_ai_services(backend_only=False)
            print("\nInterface utilisateur accessible à l'adresse: http://localhost:3000")
            print("Appuyez sur Ctrl+C pour arrêter les services.")
            
            # Attendre que l'utilisateur appuie sur Ctrl+C
            try:
                while True:
                    import time
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nArrêt demandé par l'utilisateur")
        else:
            # Mode traitement par lot
            print(f"Démarrage du traitement par lot avec le fournisseur {args.provider}...")
            pipeline.start_ai_services(backend_only=True)
            
            # Traiter la vidéo
            result = pipeline.process_with_ai_enhancement(
                args.input, 
                args.output, 
                args.prompt,
                args.provider
            )
            
            print("\nTraitement terminé!")
            print(f"Vidéo de sortie: {result['output_video']}")
            
            if result['ai_analysis']:
                print(f"Analyse IA ({result['ai_provider']}): {result['ai_analysis']}")
                print("\nContenu de l'analyse:")
                with open(result['ai_analysis'], 'r', encoding='utf-8') as f:
                    print(f"\n{f.read()[:500]}...")
    
    finally:
        # Nettoyage
        pipeline.close()
        print("Services arrêtés.")
