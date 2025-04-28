import React, { useState, useEffect } from 'react';
import './VideoViewer.css';

const VideoViewer = ({ videoId }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  useEffect(() => {
    // Réinitialiser l'état quand videoId change
    setLoading(true);
    setError('');
  }, [videoId]);
  
  const handleVideoLoaded = () => {
    setLoading(false);
  };
  
  const handleVideoError = () => {
    setLoading(false);
    setError('Erreur lors du chargement de la vidéo');
  };
  
  if (!videoId) {
    return <div className="video-error">Aucune vidéo sélectionnée</div>;
  }
  
  return (
    <div className="video-viewer">
      {loading && <div className="video-loading">Chargement de la vidéo...</div>}
      {error && <div className="video-error">{error}</div>}
      
      <video 
        controls
        onLoadedData={handleVideoLoaded}
        onError={handleVideoError}
        className={loading ? 'loading' : ''}
      >
        <source src={`http://localhost:8000/api/videos/${videoId}`} type="video/mp4" />
        Votre navigateur ne prend pas en charge la lecture de vidéos.
      </video>
      
      <div className="video-controls">
        <p>Utilisez les contrôles ci-dessus pour lire, mettre en pause ou avancer dans la vidéo.</p>
      </div>
    </div>
  );
};

export default VideoViewer;
