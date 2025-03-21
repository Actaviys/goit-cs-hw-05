cmd_inp_list = \
"""Список команд:
 sort [dirname] [copydir]: copydir - необов'язковий аргумент
 read_dir [dirname] - виводить список типів файлів в папці
 exit - вихід з програми

Є можливість запустити скрипт з аргументами:
 python [script.py] [command] [dir_name] [output_dir]
 output_dir - не обов'язковий аргумент
"""


import asyncio  # Модуль для роботи з асинхронним кодом
import aiofiles  # Бібліотека для асинхронної роботи з файлами
import argparse  # Модуль для обробки аргументів командного рядка
from pathlib import Path  # Клас для зручної роботи з файловими шляхами


#
async def copy_file(src_path, dest_folder):
    """Асинхронно копіює файл у відповідну папку на основі розширення."""
    try:
        dest_folder.mkdir(parents=True, exist_ok=True)  # Створює папку, якщо вона не існує
        dest_path = dest_folder / src_path.name  # Формує шлях до нового файлу
        
        async with aiofiles.open(src_path, 'rb') as src_file, aiofiles.open(dest_path, 'wb') as dest_file:
            while chunk := await src_file.read(4096):  # Читає файл частинами
                await dest_file.write(chunk)  # Записує у новий файл
        
        print(f"Копійовано: {src_path} -> {dest_path}")  # Виводить інформацію про копіювання
    except Exception as e:
        print(f"Помилка копіювання {src_path}: {e}")  # Виводить повідомлення про помилку


async def read_folder(source_folder, output_folder):
    """Асинхронно читає файли у вихідній папці та копіює їх за розширенням."""
    tasks = []  # Список для збереження асинхронних завдань
    for src_path in source_folder.rglob("*.*"):  # Рекурсивно знаходить всі файли
        if src_path.is_file():  # Перевіряє, чи це файл
            ext_folder = output_folder / src_path.suffix[1:]  # Створює підпапку за розширенням файлу
            tasks.append(copy_file(src_path, ext_folder))  # Додає копіювання файлу в список завдань
    await asyncio.gather(*tasks)  # Виконує всі завдання асинхронно
#



#
async def read_dir(dirname):
    """Зчитує типи файлів у вказаній папці."""
    file_types = set()
    for file in Path(dirname).rglob("*.*"):
        if file.is_file():
            file_types.add(file.suffix)
    print("Знайдені типи файлів:", ", ".join(sorted(file_types)))
#



#
def parse_arguments():
    """Обробляє аргументи командного рядка."""
    parser = argparse.ArgumentParser(description="Сортування та аналіз файлів") # Створює об'єкт ArgumentParser
    parser.add_argument("dirname", type=str, nargs="?", help="Шлях до вихідної папки") # Додає аргумент для вихідної папки
    parser.add_argument("copydir", type=str, nargs="?", help="Шлях до цільової папки") # Додає аргумент для цільової папки
    return parser.parse_args() # Повертає оброблені аргументи

def main():
    """Головна функція для обробки команд користувача."""
    args = parse_arguments() # Отримує аргументи командного рядка
    
    if args.dirname: # Якщо є аргументи то запускаю обробку 
        dirname = args.dirname
        copydir = args.copydir+"\\Sorted_Files" if args.copydir else Path.cwd() / "Sorted_Files"
        asyncio.run(read_folder(Path(dirname), Path(copydir))) # Запускає асинхронну обробку файлів
    
    else: # Якщо немає аргументів запускаю цикл для команд
        while True:
            command = input("Введіть команду: ").strip().split()
            try:
                match command[0]:
                    case "help":
                        print(cmd_inp_list)

                    case "sort":
                        dirname = command[1] if len(command) > 1 else input("Введіть папку для читання-> ")
                        copydir = command[2]+"\\Sorted_Files" if len(command) > 2 else Path.cwd() / "Sorted_Files"
                        asyncio.run(read_folder(Path(dirname), Path(copydir)))

                    case "read_dir":
                        if len(command) < 2:
                            print("Помилка: потрібно вказати шлях до папки.")
                        else:
                            asyncio.run(read_dir(command[1]))

                    case "exit": break
                    
                    case _:
                        print("Невідома команда. Використайте `help`")
            except: pass
#

                
if __name__ == "__main__":
    main()
