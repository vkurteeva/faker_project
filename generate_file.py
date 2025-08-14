from faker import Faker
import os
import random
from datetime import datetime
import sys
import re

# Инициализация Faker с русским языком
fake = Faker('ru_RU')


def load_source_text():
    """Загружает текст из файла source_text.txt в папке проекта."""
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Путь к директории скрипта
    source_file = os.path.join(script_dir, "source_text.txt")
    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            return f.read().splitlines()  # Разбиваем на строки
    except FileNotFoundError:
        print(f"Ошибка: Файл {source_file} не найден. Убедитесь, что source_text.txt находится в папке проекта.")
        return ["Образец текста недоступен. Используйте стандартный текст."]


def parse_size_input(size_input):
    """Парсит ввод размера с единицами (B, KB, MB, GB) в байты."""
    size_input = size_input.upper().strip()
    multipliers = {
        'B': 1,
        'KB': 1024,
        'MB': 1024 * 1024,
        'GB': 1024 * 1024 * 1024
    }
    match = re.match(r'(\d+(\.\d+)?)\s*([BKMG]B)?', size_input)
    if not match:
        raise ValueError(f"Неверный формат размера: {size_input}. Используйте число с единицей (B, KB, MB, GB).")

    value = float(match.group(1))  # Извлекаем числовое значение
    unit = match.group(3) or 'B'  # По умолчанию B, если единица не указана
    if unit not in multipliers:
        raise ValueError(f"Неизвестная единица измерения в {size_input}. Используйте B, KB, MB или GB.")

    return int(value * multipliers[unit])


def generate_neutral_content(size_target, format_type, source_lines):
    """Генерирует осмысленный текст с точным индикатором ожидания."""
    content = ""
    current_size = 0
    max_dots = 10  # Максимальное количество точек для индикатора
    current_progress = 0

    # Для txt: добавляем и дублируем строки из source_lines с индикатором
    if format_type == 'txt':
        lines_added = 0
        if not source_lines:
            return content
        while current_size < size_target:
            selected_line = random.choice(source_lines) + "\n"
            line_size = len(selected_line.encode('utf-8'))
            if current_size + line_size <= size_target:
                content += selected_line
                current_size += line_size
                lines_added += 1
                # Обновляем индикатор на основе текущего размера
                new_progress = min((current_size / size_target) * 100, 100)
                if new_progress >= current_progress + 10:
                    current_progress = new_progress // 10 * 10
                    progress_dots = min((current_progress / 100) * max_dots, max_dots)
                    sys.stdout.write(
                        f"\rГенерация: [{'#' * int(progress_dots) + '.' * (max_dots - int(progress_dots))}] {current_progress:.0f}%")
                    sys.stdout.flush()
            else:
                # Добавляем остаток строки, чтобы достичь размера
                remaining_bytes = size_target - current_size
                if remaining_bytes > 0 and selected_line:
                    content += selected_line[:remaining_bytes].encode('utf-8').decode('utf-8', errors='ignore')
                    current_size = size_target
        # Устанавливаем 100% при завершении
        if lines_added > 0:
            sys.stdout.write(f"\rГенерация: [{'#' * max_dots}] 100%")
            sys.stdout.flush()
        print()  # Переход на новую строку

    # Для csv: создаём строки с описанием (Имя, Пол, Возраст) с индикатором
    elif format_type == 'csv':
        header = "ItemID;Description;Status\n"
        content = header
        current_size = len(header.encode('utf-8'))
        item_id = 1
        rows_added = 1  # Учитываем заголовок
        sample_row = "1;Имя: Иван, Пол: Мужской, Возраст: 25;Активен\n"
        avg_row_length = len(sample_row.encode('utf-8'))
        total_rows = min(size_target // avg_row_length + 1, size_target // 50)  # Оценка
        while current_size < size_target:
            name = fake.first_name()  # Генерируем имя
            gender = random.choice(["Мужской", "Женский"])  # Случайный пол
            age = random.randint(15, 60)  # Случайный возраст от 15 до 60
            description = f"Имя: {name}, Пол: {gender}, Возраст: {age}"
            status = random.choice(["Активен", "Неактивен", "В ожидании"])
            row = f"{item_id};{description};{status}\n"
            row_size = len(row.encode('utf-8'))
            if current_size + row_size <= size_target:
                content += row
                current_size += row_size
                item_id += 1
                rows_added += 1
                # Обновляем индикатор на основе текущего размера
                new_progress = min((current_size / size_target) * 100, 100)
                if new_progress >= current_progress + 10:
                    current_progress = new_progress // 10 * 10
                    progress_dots = min((current_progress / 100) * max_dots, max_dots)
                    sys.stdout.write(
                        f"\rГенерация: [{'#' * int(progress_dots) + '.' * (max_dots - int(progress_dots))}] {current_progress:.0f}%")
                    sys.stdout.flush()
            else:
                # Добавляем остаток строки, чтобы достичь размера
                remaining_bytes = size_target - current_size
                if remaining_bytes > 0 and row:
                    content += row[:remaining_bytes].encode('utf-8').decode('utf-8', errors='ignore')
                    current_size = size_target
        # Устанавливаем 100% при завершении
        if rows_added > 1:  # Учитываем заголовок
            sys.stdout.write(f"\rГенерация: [{'#' * max_dots}] 100%")
            sys.stdout.flush()
        print()  # Переход на новую строку

    return content  # Возвращаем содержание с полными строками


# Пользовательский ввод
try:
    size_input = input("Введите размер файла с единицей (например, 1MB, 1024KB, 100GB, 512B): ")
    size_target = parse_size_input(size_input)

    format_type = input("Выберите формат файла (txt/csv): ").lower()
    if format_type not in ['txt', 'csv']:
        raise ValueError("Формат должен быть 'txt' или 'csv'.")

    # Загружаем текст из файла в папке проекта
    source_lines = load_source_text()

    # Формирование имени файла с датой и временем
    current_time = datetime.now().strftime("%Y-%m-%d_%H%M")
    filename = f"generated_data_{current_time}.{format_type}"

    # Генерация файла
    content = generate_neutral_content(size_target, format_type, source_lines)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

    # Проверка и вывод результата
    file_size = os.path.getsize(filename)
    print(f"Файл '{filename}' создан. Целевой размер: {size_target} байт, фактический размер: {file_size} байт "
          f"({file_size / 1024:.2f} КБ)")

except ValueError as e:
    print(f"Ошибка: {e}")
except Exception as e:
    print(f"Произошла ошибка: {e}")
