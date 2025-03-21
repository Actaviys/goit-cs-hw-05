""" 
Присутня можливість запуску скрипта з аргуметами
python [script.py] [URL]
"""

import requests  # Для завантаження файлу з URL
import re  # Для обробки тексту
import collections  # Для підрахунку частоти слів
import multiprocessing  # Для реалізації MapReduce
import matplotlib.pyplot as plt  # Для візуалізації результатів
import fitz  # PyMuPDF для обробки PDF
import io  # Для роботи з байтовими потоками
import argparse  # Модуль для обробки аргументів командного рядка


#
def get_direct_download_link(gdrive_url):
    """Перетворює Google Drive URL у прямий лінк для завантаження."""
    file_id = re.search(r'd/([^/]+)/', gdrive_url)
    if file_id:
        return f'https://drive.google.com/uc?export=download&id={file_id.group(1)}'
    return gdrive_url

def fetch_text(url):
    """Завантажує PDF-файл за URL і витягує з нього текст."""
    url = get_direct_download_link(url)  # Перетворення Google Drive посилання
    response = requests.get(url)
    response.raise_for_status()
    pdf_stream = io.BytesIO(response.content)  # Завантажуємо PDF у пам'ять
    doc = fitz.open(stream=pdf_stream, filetype="pdf")
    text = "\n".join([page.get_text() for page in doc])  # Об'єднуємо текст зі всіх сторінок
    return text
#


#
def remove_punctuation(text):
    """Розбиває текст на слова, видаляючи зайві символи."""
    words = re.findall(r'\b[a-zA-Zа-яА-ЯєЄіІїЇґҐ]+\b', text.lower())
    return words

def map_function(word):
    """Mapper-функція для створення пар (слово, 1).."""
    return (word, 1)

def reducer(word_counts):
    """Reducer-функція для підсумовування кількості входжень слів."""
    counter = collections.Counter()
    for word, count in word_counts:
        counter[word] += count
    return counter

def map_reduce(text, num_workers=4):
    """Виконує паралельний аналіз тексту за допомогою MapReduce."""
    words = remove_punctuation(text)
    with multiprocessing.Pool(num_workers) as pool:
        mapped = pool.map(map_function, words)
    return reducer(mapped)
#


#
def visualize_top_words(word_freq, top_n=15):
    """Будує горизонтальну гістограму для топ-N найчастіше вживаних слів."""
    top_words = word_freq.most_common(top_n)
    words, counts = zip(*top_words)
    plt.figure(figsize=(13, 7))
    plt.grid(True, linestyle='--', alpha=0.5)   
    # plt.barh(range(len(words)), [0] * len(words), color=(0, 0.6, 0.3))
    plt.barh(words[::-1], counts[::-1], color=(0, 0.6, 0.3)) # skyblue , #00AD17
    plt.xlabel("Частота")
    plt.ylabel("Слова")
    plt.title("Топ-15 найуживаніших слів")
    plt.show()
#


#
def parse_arguments():
    """Обробляє аргументи командного рядка."""
    parser = argparse.ArgumentParser(description="URL") # Створює об'єкт ArgumentParser
    parser.add_argument("URL", type=str, nargs="?", help="URL") # Додає аргумент для URL
    return parser.parse_args() # Повертає оброблені аргументи

def main():
    args = parse_arguments() # Отримує аргументи командного рядка
    
    try:
        if args.URL: # Якщо є аргументи то запускаю обробку 
            text = fetch_text(args.URL)
            word_freq = map_reduce(text)
            visualize_top_words(word_freq)

        else:
            url = input("Введіть URL на pdf файл для аналізу тексту \n-> ")
            text = fetch_text(url)
            word_freq = map_reduce(text)
            visualize_top_words(word_freq)
            # url = "https://drive.google.com/file/d/1mbhuAWD5lc3gSUDe0gP9ovguFI7YqG5C/view"
    except:
        print(f"Невірна URL адреса \n{args.URL or url}")
#


if __name__ == "__main__":
    main()
