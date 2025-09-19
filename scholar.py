import re
import os
from scholarly import scholarly

# --- НАСТРОЙКИ ---
# 1. Список поисковых запросов для разных тем ИСУ (Industrial Control Systems)

QUERIES = {
    'isu_lorawan_data_collection': '("industrial control system" OR "ИСУ" OR "промышленная система управления") AND ("LoRaWAN" OR "LoRa") AND ("data collection" OR "сбор данных" OR "деректерді жинау") AND ("industrial meters" OR "промышленные счетчики" OR "өндірістік есептегіштер")',
    
    'digital_twin_manufacturing': '("digital twin" OR "цифровой двойник" OR "сандық егіз") AND ("manufacturing" OR "производство" OR "өндіріс") AND ("LoRaWAN" OR "industrial IoT" OR "промышленный IoT")',
    
    'lorawan_industrial_monitoring': '("LoRaWAN" OR "LoRa") AND ("industrial monitoring" OR "промышленный мониторинг" OR "өндірістік мониторинг") AND ("meters" OR "счетчики" OR "есептегіштер") AND ("platform" OR "платформа")',
    
    'isu_digital_twin_platform': '("industrial control" OR "промышленное управление" OR "өндірістік басқару") AND ("digital twin platform" OR "платформа цифрового двойника" OR "сандық егіз платформасы") AND ("data acquisition" OR "получение данных" OR "деректерді алу")',
    
    'energy_management_lorawan': '("energy management system" OR "система управления энергией" OR "энергия басқару жүйесі") AND ("LoRaWAN" OR "IoT") AND ("industrial" OR "промышленный" OR "өндірістік")'
}

# Выберите запрос из словаря выше или введите свой
CURRENT_QUERY = 'isu_lorawan_data_collection'  # Измените на нужный ключ
QUERY = QUERIES[CURRENT_QUERY]

    
# 2. Сколько статей вы хотите получить (Google может заблокировать при больших числах)
LIMIT = 250 

# 3. Имя файла для экспорта
OUTPUT_FILENAME = 'zotero_import-energy-management-system.bib'
# --- КОНЕЦ НАСТРОЕК ---

print(f"Поиск по запросу: {QUERY}...")

try:
    # Ищем публикации
    results = scholarly.search_pubs(QUERY)
    
    bibtex_entries = []
    
    for i, result in enumerate(results):
        if i >= LIMIT:
            print(f"Достигнут лимит в {LIMIT} статей.")
            break

        # Безопасно получаем все данные из публикации
        bib = result.get('bib', {})
        title = bib.get('title', 'No Title')
        authors = bib.get('author', [])
        year = bib.get('pub_year', '')
        venue = bib.get('venue', '') # Журнал или конференция
        url = result.get('pub_url', '')
        doi = bib.get('doi', '')

        # --- НАДЁЖНАЯ ОБРАБОТКА АВТОРОВ (исправляет ошибки) ---
        main_author = "unknown"
        authors_bib = ""
        
        if isinstance(authors, list) and authors:
            # Преобразуем список авторов в строку "Author1 and Author2" для BibTeX
            authors_bib = " and ".join(authors)
            # Пытаемся получить фамилию первого автора для ключа цитирования
            try:
                # Убираем все не-буквенные символы из фамилии
                main_author = re.sub(r'[^A-Za-z]', '', authors[0].split()[-1])
            except IndexError:
                # Если у автора нет пробелов в имени, берем его целиком
                main_author = re.sub(r'[^A-Za-z]', '', authors[0])
        elif isinstance(authors, str) and authors:
            # Для старых версий, если вдруг вернется строка
             authors_bib = authors
             main_author = re.sub(r'[^A-Za-z]', '', authors.split(',')[0].split()[-1])


        # --- ГЕНЕРАЦИЯ УНИКАЛЬНОГО КЛЮЧА ЦИТИРОВАНИЯ ---
        # Например: Smith_2023_Digital
        title_word = re.sub(r'[^A-Za-z0-9]', '', title.split()[0]) if title else "paper"
        citation_key = f"{main_author}_{year}_{title_word}"

        # --- СБОРКА BIBTEX-ЗАПИСИ ---
        entry = f"@article{{{citation_key},\n"
        entry += f"  title = {{{title}}},\n"
        entry += f"  author = {{{authors_bib}}},\n"
        if year:
            entry += f"  year = {{{year}}},\n"
        if venue:
            entry += f"  journal = {{{venue}}},\n"
        if doi:
            entry += f"  doi = {{{doi}}},\n"
        if url:
            entry += f"  url = {{{url}}},\n"
        entry += "}\n\n" # Двойной перенос строки для лучшей читаемости
        
        bibtex_entries.append(entry)
        print(f"  [{i+1}/{LIMIT}] Обработана статья: {title[:60]}...")

    # --- СОХРАНЕНИЕ В ФАЙЛ ---
    if not bibtex_entries:
        print("Не найдено ни одной статьи по вашему запросу.")
    else:
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            f.writelines(bibtex_entries)
        print(f"\nГотово! Все записи сохранены в файл: {OUTPUT_FILENAME}")
        print("Теперь вы можете импортировать этот файл в Zotero.")

except Exception as e:
    print(f"\n[ОШИБКА] Произошла ошибка: {e}")
    print("\nВозможные причины и решения:")
    print("1. Google Scholar временно заблокировал ваш IP-адрес. Попробуйте снова через час или используйте VPN.")
    print("2. Проверьте ваше интернет-соединение.")
    print("3. Убедитесь, что у вас установлена правильная версия httpx: pip install httpx==0.24.1")