# AI Modal Project pour MAGI-1

Ce projet implémente une fenêtre contextuelle (modal) d'IA qui peut être intégrée au projet MAGI-1. L'application utilise React pour le frontend et FastAPI pour le backend, avec support pour plusieurs fournisseurs d'IA (OpenAI, Anthropic, DeepSeek), un visualiseur de vidéo intégré, et un générateur de vidéos à partir de descriptions textuelles.

## Structure du Projet

```
ai-modal-project/
├── backend/             # Backend FastAPI
│   ├── .env.example     # Exemple de configuration pour les variables d'environnement
│   ├── main.py          # Point d'entrée de l'API FastAPI
│   ├── video_generator.py # Module de génération de vidéos à partir de texte
│   ├── requirements.txt  # Dépendances Python
│   └── uploads/         # Dossier pour les vidéos uploadées et générées
├── frontend/            # Frontend React
│   ├── public/          # Fichiers statiques
│   ├── src/             # Code source React
│   │   ├── components/   # Composants React
│   │   │   ├── AIModal.js       # Composant de la fenêtre contextuelle
│   │   │   ├── AIModal.css      # Styles du composant modal
│   │   │   ├── VideoViewer.js   # Composant de visualisation vidéo
│   │   │   ├── VideoViewer.css  # Styles du visualiseur vidéo
│   │   │   ├── VideoGenerator.js # Composant de génération de vidéos
│   │   │   └── VideoGenerator.css # Styles du générateur de vidéos
│   │   ├── App.js     # Composant principal de l'application
│   │   ├── App.css    # Styles du composant principal
│   │   ├── index.js   # Point d'entrée React
│   │   └── index.css  # Styles globaux
│   └── package.json   # Configuration et dépendances npm
├── tests/               # Tests d'automatisation avec Selenium
│   ├── requirements.txt # Dépendances pour les tests
│   └── test_selenium.py # Tests Selenium pour la fenêtre contextuelle
├── integration.py       # Module d'intégration avec MAGI-1
└── magi_integration_example.py # Exemple d'intégration avec le pipeline MAGI-1
```

## Installation et Configuration

### Backend (FastAPI)

1. Créez un environnement virtuel Python et activez-le:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Unix/MacOS
python -m venv venv
source venv/bin/activate
```

2. Installez les dépendances:
```bash
cd ai-modal-project/backend
pip install -r requirements.txt
```

3. Configurez vos clés API pour les différents fournisseurs d'IA et services de génération vidéo:
```bash
# Copiez le fichier .env.example en .env
cp .env.example .env
# Éditez le fichier .env pour configurer vos clés API:
# - OPENAI_API_KEY=votre_clé_openai
# - ANTHROPIC_API_KEY=votre_clé_anthropic
# - DEEPSEEK_API_KEY=votre_clé_deepseek
# - REPLICATE_API_KEY=votre_clé_replicate
# - STABILITY_API_KEY=votre_clé_stability
# - RUNWAY_API_KEY=votre_clé_runway
# - DEFAULT_AI_PROVIDER=openai (ou anthropic, ou deepseek)
# - DEFAULT_VIDEO_GENERATOR=replicate (ou stability, ou runway)
```

4. Démarrez le serveur FastAPI:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (React)

1. Installez les dépendances:
```bash
cd ai-modal-project/frontend
npm install
```

2. Démarrez l'application React:
```bash
npm start
```

L'application sera accessible à l'adresse http://localhost:3000.

## Intégration avec MAGI-1

Pour intégrer ce composant dans le projet MAGI-1 existant, nous fournissons plusieurs options:

### Option 1: Utilisation du module d'intégration

Le module `integration.py` facilite l'intégration avec MAGI-1. Vous pouvez utiliser l'exemple fourni dans `magi_integration_example.py`:

```bash
# Mode interface utilisateur complète
python magi_integration_example.py --input chemin/video.mp4 --output chemin/sortie.mp4 --provider openai --ui

# Mode traitement par lot
python magi_integration_example.py --input chemin/video.mp4 --output chemin/sortie.mp4 --prompt "Analyse cette vidéo et suggère des améliorations" --provider anthropic
```

### Option 2: Intégration par iframe

Vous pouvez intégrer l'application React en tant qu'iframe dans l'application MAGI-1.

### Option 3: Importation directe des composants React

1. Copiez le dossier `frontend/src/components` dans votre projet MAGI-1
2. Importez le composant AIModal dans votre code:
```javascript
import AIModal from './path/to/components/AIModal';
import VideoViewer from './path/to/components/VideoViewer';

// Utilisation du composant
function YourComponent() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  return (
    <div>
      <button onClick={() => setIsModalOpen(true)}>Ouvrir l'Assistant IA</button>
      <AIModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </div>
  );
}
```

### Option 4: Utilisation du backend uniquement

Si vous n'avez besoin que de la fonctionnalité de traitement des requêtes IA, vous pouvez utiliser uniquement le backend FastAPI en effectuant des appels API depuis votre application existante.

## Exécution des Tests

Pour exécuter les tests Selenium:

```bash
cd ai-modal-project/tests
pip install -r requirements.txt
pytest test_selenium.py -v
```

Note: Assurez-vous que le frontend (localhost:3000) et le backend (localhost:8000) sont en cours d'exécution avant de lancer les tests.

## Fonctionnalités

### 1. Multiple Fournisseurs d'IA

Le projet prend en charge trois fournisseurs d'IA :

- **OpenAI (GPT)** : Le modèle par défaut est gpt-3.5-turbo
- **Anthropic (Claude)** : Utilise le modèle claude-3-sonnet-20240229
- **DeepSeek** : Utilise l'API DeepSeek pour des alternatives open-source

### 2. Visualiseur de Vidéo

- Upload de vidéos pour analyse par l'IA
- Lecture des vidéos directement dans l'interface
- Analyse automatique des vidéos avec les différents modèles d'IA

### 3. Générateur de Vidéos par IA

- Génération de vidéos directement à partir de descriptions textuelles
- Support pour plusieurs modèles de génération vidéo:
  - **Stable Video Diffusion** (via Replicate): Génération de vidéos de haute qualité
  - **Stability AI**: Service de génération vidéo via API Stability
  - **Runway Gen-2**: Modèle de génération vidéo avancé
- Contrôle des paramètres avancés (nombre d'images, FPS, dimensions, intensité du mouvement)
- Traitement asynchrone pour les générations de longue durée

### 4. Intégration avec MAGI-1

- Module d'intégration pour faciliter l'incorporation dans le pipeline MAGI-1
- Support pour le traitement par lot ou l'interface utilisateur interactive
- Peut être utilisé pour améliorer les résultats du traitement vidéo MAGI-1

## Sécurité

- Toutes les clés API (OpenAI, Anthropic, DeepSeek) sont stockées côté serveur dans un fichier .env et ne sont jamais exposées au client
- La validation des entrées est effectuée côté serveur
- Les en-têtes CORS sont configurés pour limiter l'accès au backend
- Les fichiers vidéo uploadés sont stockés avec des identifiants uniques pour éviter les conflits

## API Backend

Le backend expose plusieurs endpoints :

### Traitement IA

- `POST /api/process` : Traite une requête texte avec l'IA
  - Body: `{"prompt": "votre question", "provider": "openai", "max_tokens": 150}`

### Gestion Vidéo

- `POST /api/upload-video` : Upload une vidéo (multipart/form-data)
- `GET /api/videos/{video_id}` : Récupère une vidéo par son ID
- `POST /api/analyze-video` : Analyse une vidéo avec l'IA
  - Body: `{"video_id": "id_vidéo", "prompt": "question sur la vidéo", "provider": "openai"}`

### Génération de Vidéos

- `POST /api/generate-video` : Démarre une génération de vidéo asynchrone
  - Body: `{"prompt": "description de la vidéo", "provider": "replicate", "settings": {"num_frames": 24, "fps": 8}}`
  - Retourne un ID de tâche pour suivre la progression

- `GET /api/video-generation-status/{task_id}` : Vérifie le statut d'une génération
  - Retourne le statut, la progression et, une fois terminé, les informations sur la vidéo générée

- `POST /api/generate-video-sync` : Génère une vidéo en mode synchrone (pour les générations rapides)
  - Body identique à `/api/generate-video`

## Contribution

1. Forkez le dépôt
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/ma-nouvelle-fonctionnalite`)
3. Committez vos changements (`git commit -am 'Ajout d'une nouvelle fonctionnalité'`)
4. Pushez vers la branche (`git push origin feature/ma-nouvelle-fonctionnalite`)
5. Créez une Pull Request
