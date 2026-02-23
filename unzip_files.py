import os
import glob
import zipfile
import shutil
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def extract_and_remove_archive(archive_mask, extract_dir):
    """
    Находит архив по маске, распаковывает архив в папку и удаляет архив.
    """
    archives = glob.glob(archive_mask)
    if not archives:
        logger.warning(f"Архивы не найдены по маске: {archive_mask}")
        return False

    archive_path = archives[0]
    logger.info(f"Найден архив для распаковки: {archive_path}")

    if not os.path.isdir(extract_dir):
        os.makedirs(extract_dir)
        logger.info(f"Создана папка для распаковки: {extract_dir}")

    try:
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        logger.info(f"Архив успешно распакован в: {extract_dir}")
    except Exception as e:
        logger.error(f"Ошибка при распаковке архива: {e}")
        return False

    try:
        os.remove(archive_path)
        logger.info(f"Архив удалён: {archive_path}")
    except Exception as e:
        logger.error(f"Ошибка при удалении архива: {e}")

    return True

def is_file_win1251(filepath):
    """
    Проверяет, можно ли открыть файл в кодировке cp1251.
    """
    try:
        with open(filepath, 'r', encoding='cp1251') as f:
            f.read()
        return True
    except UnicodeDecodeError:
        return False
    except Exception as e:
        logger.error(f"Ошибка при проверке кодировки файла {filepath}: {e}")
        return False

def clean_file_spaces_and_special_chars(filepath):
    """
    Очищает файл от лишних пробелов и удаляет спецсимвол >.
    """
    try:
        logger.info(f"🧹 Очистка файла: {filepath}")
        
        # Читаем файл
        with open(filepath, 'r', encoding='cp1251') as f:
            lines = f.readlines()
        
        # Очищаем каждую строку
        cleaned_lines = []
        for line in lines:
            # Убираем пробелы в начале и конце
            cleaned_line = line.strip()
            
            # Удаляем все символы >
            cleaned_line = cleaned_line.replace('>', '')
            
            # Если строка не пустая, добавляем
            if cleaned_line:
                cleaned_lines.append(cleaned_line + '\n')
        
        # Записываем обратно
        with open(filepath, 'w', encoding='cp1251') as f:
            f.writelines(cleaned_lines)
            
        logger.info(f"✅ Файл очищен")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при очистке файла {filepath}: {e}")
        return False

def rename_txt_file(file_mask, new_name):
    """
    Находит файл по маске, проверяет кодировку,
    переименовывает в new_name (с заменой если файл существует)
    """
    files = glob.glob(file_mask)
    if not files:
        logger.warning(f"Файлы не найдены по маске: {file_mask}")
        return False

    old_name = files[0]
    logger.info(f"Найден файл: {old_name}")

    if is_file_win1251(old_name):
        target_name = new_name
        logger.info(f"Кодировка win-1251, переименовываю в: {target_name}")
    else:
        # Если кодировка не win-1251, сохраняем с префиксом "Ошибка кодировки"
        base_dir = os.path.dirname(new_name)
        base_name = os.path.basename(new_name)
        name_without_ext = os.path.splitext(base_name)[0]
        target_name = os.path.join(base_dir, f"Ошибка кодировки_{name_without_ext}.csv")
        logger.warning(f"Кодировка НЕ win-1251, переименовываю в: {target_name}")

    try:
        # Если файл уже существует - удаляем его (заменяем)
        if os.path.exists(target_name):
            os.remove(target_name)
            logger.info(f"🗑 Удален старый файл: {target_name}")
        
        # Переименовываем
        shutil.move(old_name, target_name)
        logger.info(f"✅ Файл переименован в: {target_name}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при переименовании: {e}")
        return False

def unzip_all_files(folder_path=None):
    """
    Распаковывает все zip-файлы и обрабатывает CSV файлы
    """
    try:
        import config
    except ImportError:
        logger.error("❌ Ошибка: не найден файл config.py")
        return 0
    
    # Определяем папку для поиска
    if folder_path is None:
        folder_path = config.DOWNLOAD_FOLDER
    
    if not os.path.exists(folder_path):
        logger.error(f"❌ Папка не найдена: {folder_path}")
        return 0
    
    # Ищем все zip файлы с маской stock_*.zip
    zip_files = list(Path(folder_path).glob("stock_*.zip"))
    
    if not zip_files:
        logger.info(f"📂 В папке {folder_path} нет zip-файлов")
        return 0
    
    logger.info(f"📦 Найдено zip-файлов: {len(zip_files)}")
    
    success_count = 0
    for zip_path in zip_files:
        try:
            # Получаем имя без расширения (stock_1, stock_50 и т.д.)
            zip_name = zip_path.stem
            extract_dir = os.path.join(folder_path, zip_name)
            
            logger.info(f"\n{'='*50}")
            logger.info(f"🔄 Обработка: {zip_path.name}")
            
            # Шаг 1: Распаковываем архив
            if extract_and_remove_archive(str(zip_path), extract_dir):
                
                # Шаг 2: Ищем CSV файл в распакованной папке
                csv_mask = os.path.join(extract_dir, "*.csv")
                csv_files = glob.glob(csv_mask)
                
                if csv_files:
                    csv_file = csv_files[0]
                    logger.info(f"📄 Найден CSV файл: {os.path.basename(csv_file)}")
                    
                    # Шаг 3: Очищаем файл от пробелов и символов >
                    if clean_file_spaces_and_special_chars(csv_file):
                        
                        # Шаг 4: Переименовываем файл в stock_1.csv и перемещаем в основную папку
                        new_name = os.path.join(folder_path, f"{zip_name}.csv")
                        if rename_txt_file(csv_mask, new_name):
                            
                            # Шаг 5: Удаляем пустую папку после перемещения
                            try:
                                if os.path.exists(extract_dir):
                                    remaining_files = os.listdir(extract_dir)
                                    if not remaining_files:
                                        os.rmdir(extract_dir)
                                        logger.info(f"🗑 Удалена пустая папка: {extract_dir}")
                                    else:
                                        logger.warning(f"⚠️ В папке остались файлы: {remaining_files}")
                            except Exception as e:
                                logger.error(f"Ошибка при удалении папки: {e}")
                            
                            success_count += 1
                            logger.info(f"✅ Файл {zip_path.name} успешно обработан")
                        else:
                            logger.error(f"❌ Ошибка при переименовании файла")
                    else:
                        logger.error(f"❌ Ошибка при очистке файла")
                else:
                    logger.error(f"❌ В архиве не найден CSV файл")
                    
                    # Показываем содержимое папки для отладки
                    if os.path.exists(extract_dir):
                        files_in_dir = os.listdir(extract_dir)
                        logger.warning(f"📂 Содержимое папки: {files_in_dir}")
            else:
                logger.error(f"❌ Ошибка при распаковке архива")
            
        except Exception as e:
            logger.error(f"❌ Ошибка при обработке {zip_path.name}: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    # Итоговая статистика
    logger.info(f"\n{'='*50}")
    logger.info(f"📊 РЕЗУЛЬТАТЫ ОБРАБОТКИ:")
    logger.info(f"   Всего архивов: {len(zip_files)}")
    logger.info(f"   ✅ Успешно обработано: {success_count}")
    logger.info(f"   ❌ Ошибок: {len(zip_files) - success_count}")
    logger.info(f"   📁 Папка: {folder_path}")
    logger.info(f"{'='*50}")
    
    return success_count