#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Главный файл: скачивает и распаковывает файлы склада
"""

import config
from stock_downloader import StockDownloader  # Этот импорт должен работать
from unzip_files import unzip_all_files
import logging
from datetime import datetime
import os
import argparse
from pathlib import Path

def setup_logging(log_folder=None):
    """Настройка логирования"""
    if log_folder is None:
        log_folder = "./logs"
    
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
        print(f"📁 Создана папка для логов: {log_folder}")
    
    log_filename = os.path.join(log_folder, f"stock_processor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return log_filename

def main():
    parser = argparse.ArgumentParser(description='Скачивание и распаковка файлов склада')
    parser.add_argument('--log-folder', '-l', help='Папка для сохранения логов')
    args = parser.parse_args()
    
    log_filename = setup_logging(args.log_folder)
    logger = logging.getLogger(__name__)
    
    logger.info("="*60)
    logger.info("🚀 ЗАПУСК ПРОЦЕССА ОБРАБОТКИ ФАЙЛОВ СКЛАДА")
    logger.info("="*60)
    
    logger.info(f"📁 Папка загрузки: {config.DOWNLOAD_FOLDER}")
    logger.info(f"📄 Файл лога: {log_filename}")
    
    if not os.path.exists(config.DOWNLOAD_FOLDER):
        logger.info(f"📁 Создание папки: {config.DOWNLOAD_FOLDER}")
        os.makedirs(config.DOWNLOAD_FOLDER)
    
    logger.info("\n📥 НАЧАЛО ЗАГРУЗКИ ФАЙЛОВ")
    downloader = StockDownloader(config)
    
    try:
        stats = downloader.download_all()
        downloader.print_summary()
        
        if stats['successful'] > 0:
            logger.info("\n📦 НАЧАЛО РАСПАКОВКИ ФАЙЛОВ")
            unzipped_count = unzip_all_files()
            
            if unzipped_count > 0:
                logger.info(f"\n✅ Распаковано файлов: {unzipped_count}")
            else:
                logger.warning("⚠️ Нет файлов для распаковки")
        else:
            logger.warning("⚠️ Загрузка не дала результатов")
            
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}", exc_info=True)
    
    logger.info("\n" + "="*60)
    logger.info("✅ ПРОЦЕСС ЗАВЕРШЕН")
    logger.info("="*60)

if __name__ == "__main__":
    main()