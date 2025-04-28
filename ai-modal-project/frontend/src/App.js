import React, { useState } from 'react';
import './App.css';
import AIModal from './components/AIModal';
import VideoGenerator from './components/VideoGenerator';

function App() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('home');

  const openModal = () => setIsModalOpen(true);
  const closeModal = () => setIsModalOpen(false);

  const renderContent = () => {
    switch (activeTab) {
      case 'home':
        return (
          <>
            <div className="demo-section">
              <h2>Assistant IA Multi-modal</h2>
              <p>
                Cliquez sur le bouton ci-dessous pour ouvrir la fenêtre contextuelle et interagir avec l'IA.
                Cette application permet d'utiliser plusieurs modèles d'IA (OpenAI, Anthropic, DeepSeek) et d'analyser des vidéos.
              </p>
              <button 
                className="btn btn-primary"
                onClick={openModal}
              >
                Ouvrir l'Assistant IA
              </button>
            </div>

            <div className="features-section">
              <h2>Fonctionnalités</h2>
              <ul>
                <li>Interface utilisateur réactive avec React</li>
                <li>Fenêtre contextuelle (modal) élégante</li>
                <li>Support de multiples fournisseurs d'IA (OpenAI, Anthropic, DeepSeek)</li>
                <li>Analyse de vidéos avec l'IA</li>
                <li>Génération de vidéos à partir de descriptions textuelles</li>
                <li>Sécurité avec stockage des clés d'API côté serveur</li>
              </ul>
            </div>
          </>
        );
      case 'video-generator':
        return <VideoGenerator />;
      default:
        return <p>Page non trouvée.</p>;
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>MAGI-1 AI Assistant</h1>
        <nav className="main-nav">
          <button 
            className={`nav-button ${activeTab === 'home' ? 'active' : ''}`} 
            onClick={() => setActiveTab('home')}
          >
            Accueil
          </button>
          <button 
            className={`nav-button ${activeTab === 'video-generator' ? 'active' : ''}`} 
            onClick={() => setActiveTab('video-generator')}
          >
            Générateur de Vidéos
          </button>
        </nav>
      </header>
      <main className="container">
        {renderContent()}
      </main>

      {/* Fenêtre contextuelle IA */}
      <AIModal isOpen={isModalOpen} onClose={closeModal} />
    </div>
  );
}

export default App;
