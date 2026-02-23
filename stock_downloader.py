import os
import requests
from urllib.parse import urlparse
import time
from datetime import datetime
from typing import Dict, List, Optional
import config
import logging

logger = logging.getLogger(__name__)

class StockDownloader:
    """
    Класс для скачивания файлов наличия на складе
    """
    
    def __init__(self, config_module):
        """
        Инициализация загрузчика
        
        Args:
            config_module: модуль с конфигурацией
        """
        self.config = config_module
        self.stats = {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'start_time': None,
            'end_time': None
        }
        self.stock_urls = self._load_urls_from_config()
        
    def _load_urls_from_config(self) -> List[Dict]:
        """
        Загружает список URL из конфигурации
        
        Returns:
            List[Dict]: список словарей с name и url
        """
        urls = []
        
        # Проверяем наличие STOCK_URLS в конфиге
        if hasattr(self.config, 'STOCK_URLS') and self.config.STOCK_URLS:
            urls = self.config.STOCK_URLS
            logger.info(f"📄 Загружено складов из конфига: {len(urls)}")
            
            # Выводим список загруженных складов
            if urls:
                logger.info("📋 Список складов:")
                for i, stock in enumerate(urls, 1):
                    logger.info(f"   {i}. {stock['name']}")
        else:
            logger.warning("⚠️ В конфиге нет STOCK_URLS")
        
        return urls
    
    def _ensure_folder_exists(self, folder_path: str) -> None:
        """Создает папку для загрузки, если она не существует"""
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            logger.info(f"📁 Создана папка: {folder_path}")
    
    def _get_filename_from_url(self, url: str, default_name: str = "stock_file") -> str:
        """Извлекает имя файла из URL"""
        # Пробуем извлечь StockId
        if 'StockId=' in url:
            stock_id = url.split('StockId=')[1].split('&')[0]
            return f"stock_{stock_id}.zip"
        
        # Возвращаем имя по умолчанию с временной меткой
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{default_name}_{timestamp}.zip"
    
    def _format_size(self, size_bytes: int) -> str:
        """Форматирует размер файла в человекочитаемый вид"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    def download_file(self, url_info: Dict, index: int, total: int) -> bool:
        """
        Скачивает один файл
        
        Args:
            url_info: информация о URL (name, url)
            index: индекс текущего файла
            total: общее количество файлов
            
        Returns:
            bool: успешно ли скачан файл
        """
        url = url_info['url']
        name = url_info.get('name', f'Файл {index}')
        
        try:
            # Получаем имя файла
            filename = self._get_filename_from_url(url)
            file_path = os.path.join(self.config.DOWNLOAD_FOLDER, filename)
            
            # Заголовки для запроса
            headers = {
                'User-Agent': self.config.DOWNLOAD_SETTINGS.get('user_agent', 'Mozilla/5.0')
            }
            
            logger.info(f"[{index}/{total}] 📥 Скачивание: {name}")
            logger.info(f"   URL: {url}")
            logger.info(f"   Файл: {filename}")
            
            # Скачиваем файл
            response = requests.get(
                url, 
                headers=headers, 
                stream=True, 
                timeout=self.config.DOWNLOAD_SETTINGS.get('timeout', 30)
            )
            response.raise_for_status()
            
            # Получаем размер файла
            total_size = int(response.headers.get('content-length', 0))
            if total_size > 0:
                logger.info(f"   Размер: {self._format_size(total_size)}")
            
            # Сохраняем файл
            with open(file_path, 'wb') as file:
                if total_size == 0:
                    file.write(response.content)
                else:
                    downloaded = 0
                    for chunk in response.iter_content(
                        chunk_size=self.config.DOWNLOAD_SETTINGS.get('chunk_size', 8192)
                    ):
                        if chunk:
                            file.write(chunk)
                            downloaded += len(chunk)
                            
                            # Показываем прогресс
                            if downloaded % (1024*1024) < 8192:  # Логируем каждый мегабайт
                                logger.debug(f"   Прогресс: {downloaded/total_size*100:.1f}%")
                    
            logger.info(f"   ✅ Файл сохранен: {file_path}")
            return True
            
        except requests.exceptions.Timeout:
            logger.error(f"❌ Таймаут при скачивании {url}")
        except requests.exceptions.ConnectionError:
            logger.error(f"❌ Ошибка соединения при скачивании {url}")
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ HTTP ошибка: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Ошибка при скачивании: {e}")
        except Exception as e:
            logger.error(f"❌ Непредвиденная ошибка: {e}")
        
        return False
    
    def download_all(self) -> Dict:
        """
        Скачивает все файлы из конфигурации
        
        Returns:
            Dict: статистика загрузки
        """
        if not self.stock_urls:
            logger.error("❌ Нет URL для скачивания")
            return self.stats
        
        self.stats['start_time'] = datetime.now()
        self.stats['total'] = len(self.stock_urls)
        
        # Создаем папку для загрузки
        self._ensure_folder_exists(self.config.DOWNLOAD_FOLDER)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🚀 Начало загрузки файлов склада")
        logger.info(f"📊 Всего файлов: {self.stats['total']}")
        logger.info(f"📁 Папка сохранения: {self.config.DOWNLOAD_FOLDER}")
        logger.info(f"{'='*60}")
        
        # Скачиваем файлы
        for i, url_info in enumerate(self.stock_urls, 1):
            success = self.download_file(url_info, i, self.stats['total'])
            
            if success:
                self.stats['successful'] += 1
            else:
                self.stats['failed'] += 1
            
            # Пауза между загрузками
            if i < self.stats['total']:
                delay = self.config.DOWNLOAD_SETTINGS.get('delay_between_downloads', 1)
                if delay > 0:
                    logger.info(f"⏳ Ожидание {delay} сек...")
                    time.sleep(delay)
        
        self.stats['end_time'] = datetime.now()
        return self.stats
    
    def print_summary(self) -> None:
        """Выводит итоговую статистику"""
        duration = self.stats['end_time'] - self.stats['start_time']
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ ЗАГРУЗКА ЗАВЕРШЕНА!")
        logger.info(f"{'='*60}")
        logger.info(f"📊 Статистика:")
        logger.info(f"   Всего файлов: {self.stats['total']}")
        logger.info(f"   ✅ Успешно: {self.stats['successful']}")
        logger.info(f"   ❌ Ошибок: {self.stats['failed']}")
        logger.info(f"   ⏱ Время выполнения: {duration.total_seconds():.1f} сек")
        logger.info(f"📁 Файлы сохранены: {os.path.abspath(self.config.DOWNLOAD_FOLDER)}")
        logger.info(f"{'='*60}")