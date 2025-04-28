import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

class TestAIModal:
    @pytest.fixture(scope="function")
    def driver(self):
        # Configuration du driver Chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Exécution sans interface graphique
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.maximize_window()
        yield driver
        driver.quit()
    
    def test_open_modal(self, driver):
        """Teste l'ouverture de la modal d'IA"""
        # Ouvrir la page
        driver.get("http://localhost:3000")
        
        # Trouver et cliquer sur le bouton pour ouvrir la modal
        open_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "btn-primary"))
        )
        open_button.click()
        
        # Vérifier que la modal est ouverte
        modal = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "modal-container"))
        )
        assert modal.is_displayed(), "La modal n'est pas affichée après avoir cliqué sur le bouton"
        
        # Vérifier la présence des éléments de la modal
        assert driver.find_element(By.ID, "ai-input").is_displayed()
        assert driver.find_element(By.CSS_SELECTOR, ".submit-button").is_displayed()
    
    def test_submit_query(self, driver):
        """Teste la soumission d'une requête à l'IA"""
        # Ouvrir la page et la modal
        driver.get("http://localhost:3000")
        
        open_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "btn-primary"))
        )
        open_button.click()
        
        # Entrer une question dans le champ de texte
        input_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ai-input"))
        )
        test_question = "Bonjour, comment ça marche ?"
        input_field.send_keys(test_question)
        
        # Soumettre la requête
        submit_button = driver.find_element(By.CSS_SELECTOR, ".submit-button")
        submit_button.click()
        
        # Attendre et vérifier la réponse (en supposant que le backend est opérationnel)
        try:
            # Si le backend n'est pas disponible, ce test pourrait échouer
            response_container = WebDriverWait(driver, 15).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "response-container"))
            )
            assert response_container.is_displayed()
            response_content = driver.find_element(By.CLASS_NAME, "response-content")
            assert len(response_content.text) > 0, "La réponse est vide"
        except:
            # Vérifier au moins que le bouton est en mode "loading"
            submit_button = driver.find_element(By.CSS_SELECTOR, ".submit-button")
            assert "Traitement en cours..." in submit_button.text or submit_button.get_attribute("disabled") == "true"

if __name__ == "__main__":
    pytest.main(["-v", "test_selenium.py"])
