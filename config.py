"""
Конфигурационный файл для скрипта загрузки файлов склада
"""

# Список URL для скачивания файлов наличия на складе
# Получите ключи доступа у вашего менеджера
STOCK_URLS = [
    {
       "name": "Центральный склад",
       "url": "https://mikado-parts.ru/api/Price/GetPrice?StockId=1&Key=1ED5650E-0A7D-4FE9-9A9D-F27550201753"
    },
    {
        "name": "Москва", 
        "url": "https://mikado-parts.ru/api/Price/GetPrice?StockId=50&Key=1ED5650E-0A7D-4FE9-9A9D-F27550201753"
    },
    {
        "name": "Москва 2",
        "url": "https://mikado-parts.ru/api/Price/GetPrice?StockId=77&Key=1ED5650E-0A7D-4FE9-9A9D-F27550201753"
    },
    {
        "name": "Орел",
        "url": "https://mikado-parts.ru/api/Price/GetPrice?StockId=57&Key=1ED5650E-0A7D-4FE9-9A9D-F27550201753"
    },
    {
        "name": "Смоленск",
        "url": "https://mikado-parts.ru/api/Price/GetPrice?StockId=67&Key=1ED5650E-0A7D-4FE9-9A9D-F27550201753"
    },
    {
        "name": "Курск",
        "url": "https://mikado-parts.ru/api/Price/GetPrice?StockId=46&Key=1ED5650E-0A7D-4FE9-9A9D-F27550201753"
    },
    {
        "name": "Белгород",
        "url": "https://mikado-parts.ru/api/Price/GetPrice?StockId=31&Key=1ED5650E-0A7D-4FE9-9A9D-F27550201753"
    },
    {
        "name": "Самара",
        "url": "https://mikado-parts.ru/api/Price/GetPrice?StockId=63&Key=1ED5650E-0A7D-4FE9-9A9D-F27550201753"
    }

]

# Папка для сохранения файлов
DOWNLOAD_FOLDER = r"\\xen\DATAW\Dropbox\InterParts\Berloga\RU\RU77\R77A7"  # Замените на свой путь

# Настройки загрузки
DOWNLOAD_SETTINGS = {
    "timeout": 30,  # Таймаут запроса в секундах
    "chunk_size": 8192,  # Размер чанка для скачивания
    "delay_between_downloads": 1,  # Задержка между загрузками в секундах
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# Настройки логирования
LOGGING_SETTINGS = {
    "show_progress_bar": True,
    "show_file_size": True,
    "save_log_to_file": True,
    "log_file_path": "download_log.txt"  # относительный путь
}

# НАСТРОЙКИ ЛОГИРОВАНИЯ ОСНОВНОГО ПРОЦЕССА
LOG_CONFIG = {
    "folder": r"\logs",  # папка для логов
    # "folder": "./logs",   # или относительный путь
    # "folder": os.path.join(DOWNLOAD_FOLDER, "logs"),  # папка logs рядом с файлами
    "filename_pattern": "stock_processor_%Y%m%d_%H%M%S.log",  # шаблон имени
    "level": "INFO",  # уровень логирования: DEBUG, INFO, WARNING, ERROR
}
