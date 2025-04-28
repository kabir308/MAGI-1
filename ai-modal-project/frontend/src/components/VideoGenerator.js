import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './VideoGenerator.css';
import VideoViewer from './VideoViewer';

const VideoGenerator = () => {
  const [prompt, setPrompt] = useState('');
  const [provider, setProvider] = useState('replicate');
  const [settings, setSettings] = useState({
    // Replicate default settings
    num_frames: 24,
    fps: 8,
    width: 576,
    height: 320,
    motion_bucket_id: 127
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [taskId, setTaskId] = useState(null);
  const [taskStatus, setTaskStatus] = useState(null);
  const [generatedVideo, setGeneratedVideo] = useState(null);
  const [statusInterval, setStatusInterval] = useState(null);
  const [showAdvancedSettings, setShowAdvancedSettings] = useState(false);

  // Settings templates par modèle
  const settingsTemplates = {
    replicate: {
      num_frames: 24,
      fps: 8,
      width: 576,
      height: 320,
      motion_bucket_id: 127
    },
    stability: {
      duration: 3,
      width: 768,
      height: 432,
      cfg_scale: 7.5
    },
    runway: {
      num_steps: 50,
      fps: 24
    }
  };

  // Mettre à jour les paramètres quand le fournisseur change
  useEffect(() => {
    setSettings(settingsTemplates[provider] || settingsTemplates.replicate);
  }, [provider]);

  // Vérifier le statut de la tâche périodiquement
  useEffect(() => {
    if (taskId && !statusInterval) {
      const interval = setInterval(checkTaskStatus, 2000);
      setStatusInterval(interval);
    }

    return () => {
      if (statusInterval) {
        clearInterval(statusInterval);
      }
    };
  }, [taskId]);

  // Arrêter l'intervalle quand la tâche est terminée
  useEffect(() => {
    if (taskStatus && (taskStatus.status === 'completed' || taskStatus.status === 'failed')) {
      if (statusInterval) {
        clearInterval(statusInterval);
        setStatusInterval(null);
      }

      if (taskStatus.status === 'completed' && taskStatus.video_info) {
        setGeneratedVideo(taskStatus.video_info);
      }
    }
  }, [taskStatus]);

  // Vérifier le statut de la tâche
  const checkTaskStatus = async () => {
    if (!taskId) return;

    try {
      const response = await axios.get(`http://localhost:8000/api/video-generation-status/${taskId}`);
      setTaskStatus(response.data);
    } catch (err) {
      console.error('Erreur lors de la vérification du statut:', err);
      setError('Erreur lors de la vérification du statut de la génération');
      
      if (statusInterval) {
        clearInterval(statusInterval);
        setStatusInterval(null);
      }
    }
  };

  // Générer une vidéo
  const handleGenerateVideo = async (e) => {
    e.preventDefault();
    if (!prompt.trim()) {
      setError('Veuillez entrer une description pour la vidéo');
      return;
    }

    setLoading(true);
    setError('');
    setTaskId(null);
    setTaskStatus(null);
    setGeneratedVideo(null);

    try {
      // Utiliser l'API asynchrone pour les longues générations
      const response = await axios.post('http://localhost:8000/api/generate-video', {
        prompt: prompt,
        provider: provider,
        settings: settings
      });

      setTaskId(response.data.task_id);
    } catch (err) {
      console.error('Erreur lors de la génération de vidéo:', err);
      setError(`Erreur: ${err.response?.data?.detail || 'Impossible de communiquer avec le serveur'}`);
      setLoading(false);
    }
  };

  // Mettre à jour un paramètre de configuration
  const updateSetting = (key, value) => {
    setSettings({
      ...settings,
      [key]: value
    });
  };

  // Générer les champs de paramètres selon le fournisseur
  const renderSettings = () => {
    if (!showAdvancedSettings) return null;

    switch (provider) {
      case 'replicate':
        return (
          <div className="settings-fields">
            <div className="settings-field">
              <label htmlFor="num_frames">Nombre d'images:</label>
              <input
                id="num_frames"
                type="number"
                min="16"
                max="48"
                value={settings.num_frames}
                onChange={(e) => updateSetting('num_frames', parseInt(e.target.value))}
              />
            </div>
            <div className="settings-field">
              <label htmlFor="fps">Images/seconde:</label>
              <input
                id="fps"
                type="number"
                min="1"
                max="30"
                value={settings.fps}
                onChange={(e) => updateSetting('fps', parseInt(e.target.value))}
              />
            </div>
            <div className="settings-field">
              <label htmlFor="width">Largeur:</label>
              <input
                id="width"
                type="number"
                min="320"
                max="1024"
                step="64"
                value={settings.width}
                onChange={(e) => updateSetting('width', parseInt(e.target.value))}
              />
            </div>
            <div className="settings-field">
              <label htmlFor="height">Hauteur:</label>
              <input
                id="height"
                type="number"
                min="320"
                max="1024"
                step="64"
                value={settings.height}
                onChange={(e) => updateSetting('height', parseInt(e.target.value))}
              />
            </div>
            <div className="settings-field">
              <label htmlFor="motion_bucket_id">Intensité du mouvement:</label>
              <input
                id="motion_bucket_id"
                type="range"
                min="1"
                max="255"
                value={settings.motion_bucket_id}
                onChange={(e) => updateSetting('motion_bucket_id', parseInt(e.target.value))}
              />
              <span>{settings.motion_bucket_id}</span>
            </div>
          </div>
        );
      case 'stability':
        return (
          <div className="settings-fields">
            <div className="settings-field">
              <label htmlFor="duration">Durée (secondes):</label>
              <input
                id="duration"
                type="number"
                min="1"
                max="10"
                value={settings.duration}
                onChange={(e) => updateSetting('duration', parseInt(e.target.value))}
              />
            </div>
            <div className="settings-field">
              <label htmlFor="stability_width">Largeur:</label>
              <input
                id="stability_width"
                type="number"
                min="384"
                max="1024"
                step="64"
                value={settings.width}
                onChange={(e) => updateSetting('width', parseInt(e.target.value))}
              />
            </div>
            <div className="settings-field">
              <label htmlFor="stability_height">Hauteur:</label>
              <input
                id="stability_height"
                type="number"
                min="384"
                max="1024"
                step="64"
                value={settings.height}
                onChange={(e) => updateSetting('height', parseInt(e.target.value))}
              />
            </div>
            <div className="settings-field">
              <label htmlFor="cfg_scale">Échelle de guidage:</label>
              <input
                id="cfg_scale"
                type="range"
                min="1"
                max="15"
                step="0.5"
                value={settings.cfg_scale}
                onChange={(e) => updateSetting('cfg_scale', parseFloat(e.target.value))}
              />
              <span>{settings.cfg_scale}</span>
            </div>
          </div>
        );
      case 'runway':
        return (
          <div className="settings-fields">
            <div className="settings-field">
              <label htmlFor="num_steps">Étapes de diffusion:</label>
              <input
                id="num_steps"
                type="number"
                min="20"
                max="100"
                value={settings.num_steps}
                onChange={(e) => updateSetting('num_steps', parseInt(e.target.value))}
              />
            </div>
            <div className="settings-field">
              <label htmlFor="runway_fps">Images/seconde:</label>
              <input
                id="runway_fps"
                type="number"
                min="15"
                max="60"
                value={settings.fps}
                onChange={(e) => updateSetting('fps', parseInt(e.target.value))}
              />
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  // Afficher le statut de génération
  const renderGenerationStatus = () => {
    if (!taskId || !taskStatus) return null;

    const progress = taskStatus.progress || 0;
    const progressPercent = Math.round(progress * 100);

    return (
      <div className="generation-status">
        <h3>Statut de la génération</h3>
        <div className="status-details">
          <p>
            <strong>État:</strong> {
              taskStatus.status === 'pending' ? 'En attente' :
              taskStatus.status === 'running' ? 'En cours de génération' :
              taskStatus.status === 'completed' ? 'Terminé' :
              taskStatus.status === 'failed' ? 'Échec' : 'Inconnu'
            }
          </p>
          
          {taskStatus.status === 'running' && (
            <div className="progress-bar-container">
              <div 
                className="progress-bar" 
                style={{width: `${progressPercent}%`}}
              ></div>
              <span className="progress-text">{progressPercent}%</span>
            </div>
          )}

          {taskStatus.status === 'failed' && taskStatus.error && (
            <div className="generation-error">
              <p>Erreur: {taskStatus.error}</p>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="video-generator-container">
      <h2>Générateur de Vidéos IA</h2>
      <p className="generator-description">
        Créez des vidéos directement à partir de descriptions textuelles grâce à l'intelligence artificielle.
      </p>

      <form onSubmit={handleGenerateVideo} className="generator-form">
        <div className="input-group">
          <label htmlFor="prompt-input">Description de la vidéo:</label>
          <textarea
            id="prompt-input"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Décrivez la vidéo que vous souhaitez générer..."
            rows={4}
            disabled={loading}
          />
        </div>

        <div className="provider-selector">
          <label htmlFor="provider-select">Générateur de vidéo:</label>
          <select 
            id="provider-select" 
            value={provider} 
            onChange={(e) => setProvider(e.target.value)}
            disabled={loading}
          >
            <option value="replicate">Stable Video Diffusion</option>
            <option value="stability">Stability AI</option>
            <option value="runway">Runway Gen-2</option>
          </select>
        </div>

        <div className="settings-toggle">
          <button
            type="button"
            className="btn btn-secondary settings-toggle-button"
            onClick={() => setShowAdvancedSettings(!showAdvancedSettings)}
            disabled={loading}
          >
            {showAdvancedSettings ? 'Masquer les paramètres avancés' : 'Afficher les paramètres avancés'}
          </button>
        </div>

        {renderSettings()}

        <div className="button-group">
          <button 
            type="submit" 
            className="btn btn-primary generate-button"
            disabled={loading || !prompt.trim()}
          >
            {loading ? 'Génération en cours...' : 'Générer la vidéo'}
          </button>
        </div>
      </form>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {renderGenerationStatus()}

      {generatedVideo && (
        <div className="generated-video-container">
          <h3>Vidéo générée</h3>
          <div className="video-info">
            <p><strong>Prompt:</strong> {prompt}</p>
            <p><strong>Générateur:</strong> {provider}</p>
          </div>
          <VideoViewer videoId={generatedVideo.file_id} />
        </div>
      )}
    </div>
  );
};

export default VideoGenerator;
