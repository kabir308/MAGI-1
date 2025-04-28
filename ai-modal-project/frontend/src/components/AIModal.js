import React, { useState, useRef } from 'react';
import axios from 'axios';
import './AIModal.css';
import VideoViewer from './VideoViewer';

const AIModal = ({ isOpen, onClose }) => {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [provider, setProvider] = useState('openai');
  const [video, setVideo] = useState(null);
  const [showVideoViewer, setShowVideoViewer] = useState(false);
  const fileInputRef = useRef(null);

  // Fonction pour gérer la soumission de la requête à l'API
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setLoading(true);
    setError('');
    
    try {
      let endpoint = 'http://localhost:8000/api/process';
      let requestData = {
        prompt: prompt,
        provider: provider
      };
      
      // Si une vidéo est sélectionnée, utiliser l'API d'analyse vidéo
      if (video) {
        endpoint = 'http://localhost:8000/api/analyze-video';
        requestData = {
          video_id: video.file_id,
          prompt: prompt,
          provider: provider
        };
      }
      
      const result = await axios.post(endpoint, requestData);
      
      setResponse(result.data.result);
    } catch (err) {
      console.error('Erreur lors de la requête API:', err);
      setError(`Erreur: ${err.response?.data?.detail || 'Communication avec l\'API impossible'}`);
    } finally {
      setLoading(false);
    }
  };
  
  // Fonction pour gérer l'upload de vidéo
  const handleVideoUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    // Vérifier que c'est bien une vidéo
    if (!file.type.startsWith('video/')) {
      setError('Veuillez sélectionner un fichier vidéo valide.');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const result = await axios.post('http://localhost:8000/api/upload-video', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      setVideo(result.data);
      setShowVideoViewer(true);
    } catch (err) {
      console.error('Erreur lors de l\'upload de la vidéo:', err);
      setError('Erreur lors de l\'upload de la vidéo. Veuillez réessayer.');
    } finally {
      setLoading(false);
    }
  };
  
  // Déclencher le click sur l'input file caché
  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

  // Si le modal n'est pas ouvert, ne rien afficher
  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-container">
        <div className="modal-header">
          <h2>Assistant IA</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        <div className="modal-body">
          {/* Sélection du fournisseur d'IA */}
          <div className="provider-selector">
            <label htmlFor="provider-select">Fournisseur d'IA:</label>
            <select 
              id="provider-select" 
              value={provider} 
              onChange={(e) => setProvider(e.target.value)}
              disabled={loading}
            >
              <option value="openai">OpenAI</option>
              <option value="anthropic">Anthropic (Claude)</option>
              <option value="deepseek">DeepSeek</option>
            </select>
          </div>
          
          {/* Upload de vidéo */}
          <div className="video-upload-section">
            <button 
              type="button" 
              className="btn btn-secondary upload-button"
              onClick={triggerFileInput}
              disabled={loading}
            >
              Uploader une vidéo pour analyse
            </button>
            <input 
              type="file" 
              ref={fileInputRef}
              onChange={handleVideoUpload}
              accept="video/*"
              style={{ display: 'none' }}
            />
            {video && (
              <div className="video-info">
                <span>Vidéo sélectionnée: {video.filename}</span>
                <button 
                  type="button" 
                  className="btn btn-secondary view-video-button"
                  onClick={() => setShowVideoViewer(!showVideoViewer)}
                >
                  {showVideoViewer ? 'Masquer vidéo' : 'Voir vidéo'}
                </button>
              </div>
            )}
          </div>
          
          {/* Visualiseur de vidéo */}
          {showVideoViewer && video && (
            <VideoViewer videoId={video.file_id} />
          )}
          
          <form onSubmit={handleSubmit}>
            <div className="input-group">
              <textarea
                id="ai-input"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder={video ? "Posez une question à propos de cette vidéo..." : "Posez votre question..."}
                rows={4}
                disabled={loading}
              />
            </div>
            
            <div className="button-group">
              <button 
                type="submit" 
                className="btn btn-primary submit-button"
                disabled={loading || !prompt.trim()}
              >
                {loading ? 'Traitement en cours...' : 'Envoyer'}
              </button>
            </div>
          </form>
          
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}
          
          {response && (
            <div className="response-container">
              <h3>Réponse:</h3>
              <div className="response-content">
                {response}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AIModal;
