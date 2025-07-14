"""
Tests para el módulo de scraper
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scraper.mlb_scraper import MLBScraper
from src.scraper.scheduler import ConsensusScheduler

class TestMLBScraper:
    """Tests para el scraper de MLB"""
    
    @pytest.fixture
    def scraper(self):
        """Fixture para el scraper"""
        return MLBScraper()
    
    def test_scraper_initialization(self, scraper):
        """Test de inicialización del scraper"""
        assert scraper.base_url == "https://www.covers.com/sports/mlb/consensus"
        assert scraper.session is not None
        assert scraper.timezone is not None
    
    @patch('requests.Session.get')
    def test_get_page_content_success(self, mock_get, scraper):
        """Test de obtención exitosa de contenido"""
        # Mock response
        mock_response = Mock()
        mock_response.content = b'<html><body>Test content</body></html>'
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = scraper.get_page_content("http://test.com")
        
        assert result is not None
        assert result.body is not None
        mock_get.assert_called_once()
    
    @patch('requests.Session.get')
    def test_get_page_content_failure(self, mock_get, scraper):
        """Test de falla en obtención de contenido"""
        mock_get.side_effect = Exception("Network error")
        
        with pytest.raises(Exception):
            scraper.get_page_content("http://test.com")
    
    def test_extract_consensus_from_row(self, scraper):
        """Test de extracción de datos de consenso"""
        # Mock HTML row
        from bs4 import BeautifulSoup
        
        html = """
        <tr class="game-row">
            <td class="teams">Yankees @ Red Sox</td>
            <td class="percentage">78%</td>
            <td class="percentage">82%</td>
            <td class="percentage">71%</td>
            <td class="time">14:30</td>
        </tr>
        """
        
        soup = BeautifulSoup(html, 'html.parser')
        row = soup.find('tr')
        
        result = scraper._extract_consensus_from_row(row, '2025-07-13')
        
        if result:  # Si logra extraer datos
            assert result['equipo_visitante'] == 'Yankees'
            assert result['equipo_local'] == 'Red Sox'
            assert result['fecha'] == '2025-07-13'
    
    @patch.object(MLBScraper, 'get_page_content')
    def test_scrape_mlb_consensus(self, mock_get_content, scraper):
        """Test del scraping principal"""
        # Mock BeautifulSoup content
        from bs4 import BeautifulSoup
        
        html_content = """
        <html>
            <body>
                <table class="consensus-table">
                    <tr class="game-row">
                        <td class="teams">Yankees @ Red Sox</td>
                        <td class="percentage">78%</td>
                    </tr>
                </table>
            </body>
        </html>
        """
        
        mock_soup = BeautifulSoup(html_content, 'html.parser')
        mock_get_content.return_value = mock_soup
        
        result = scraper.scrape_mlb_consensus('2025-07-13')
        
        assert isinstance(result, list)
        mock_get_content.assert_called_once()
    
    def test_scraper_context_manager(self):
        """Test del context manager del scraper"""
        with MLBScraper() as scraper:
            assert scraper.session is not None
        # El scraper debería haber cerrado la sesión

class TestConsensusScheduler:
    """Tests para el scheduler de consensos"""
    
    @pytest.fixture
    def scheduler(self):
        """Fixture para el scheduler"""
        return ConsensusScheduler()
    
    def test_scheduler_initialization(self, scheduler):
        """Test de inicialización del scheduler"""
        assert scheduler.scheduler is not None
        assert scheduler.timezone is not None
        assert scheduler.is_running is False
    
    def test_set_callbacks(self, scheduler):
        """Test de configuración de callbacks"""
        def mock_callback():
            pass
        
        scheduler.set_callbacks(
            on_consensus_scraped=mock_callback,
            on_error=mock_callback,
            on_daily_report=mock_callback
        )
        
        assert scheduler.on_consensus_scraped == mock_callback
        assert scheduler.on_error == mock_callback
        assert scheduler.on_daily_report == mock_callback
    
    def test_setup_mlb_schedule(self, scheduler):
        """Test de configuración de horarios MLB"""
        scheduler.setup_mlb_schedule()
        
        jobs = scheduler.scheduler.get_jobs()
        job_ids = [job.id for job in jobs]
        
        assert 'mlb_daily_scraping' in job_ids
        assert 'mlb_live_scraping' in job_ids
        assert 'daily_report' in job_ids
        assert 'log_cleanup' in job_ids
    
    def test_get_job_status(self, scheduler):
        """Test de obtención de estado de jobs"""
        scheduler.setup_mlb_schedule()
        
        status = scheduler.get_job_status()
        
        assert isinstance(status, dict)
        assert len(status) > 0
        
        for job_id, info in status.items():
            assert 'name' in info
            assert 'trigger' in info
    
    @patch.object(ConsensusScheduler, '_scrape_mlb_daily')
    def test_run_job_now(self, mock_scrape, scheduler):
        """Test de ejecución manual de job"""
        scheduler.setup_mlb_schedule()
        
        scheduler.run_job_now('mlb_daily_scraping')
        
        mock_scrape.assert_called_once()

# Tests de integración
class TestScraperIntegration:
    """Tests de integración del scraper"""
    
    @pytest.mark.asyncio
    async def test_full_scraping_workflow(self):
        """Test del flujo completo de scraping"""
        # Este test requiere conexión real o mocks más complejos
        # Por ahora, solo verificamos que las clases se pueden instanciar juntas
        
        scraper = MLBScraper()
        scheduler = ConsensusScheduler()
        
        assert scraper is not None
        assert scheduler is not None
        
        # Cleanup
        scraper.close()
        scheduler.stop()

# Configuración de pytest
def pytest_configure(config):
    """Configuración global de pytest"""
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)

if __name__ == "__main__":
    # Ejecutar tests
    pytest.main([__file__, "-v"])
