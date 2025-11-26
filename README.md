Простое консольное приложение для управления задачами
Хранение данных — в локальном tasks.json.
Работает без сторонних библиотек, только стандартный Python.


Возможности
Добавление задачи
Обновление описания
Удаление
Изменение статуса (todo, in-progress, done)
Просмотр всех задач или по статусу
Хранение в JSON-файле


Установите python 3.8+ 

Все команды 
# добавить задачу
python task_cli.py add "Buy groceries"

# посмотреть все задачи
python task_cli.py list

# изменить описание задачи с id=1
python task_cli.py update 1 "Buy groceries and cook dinner"

# отметить как в процессе
python task_cli.py mark-in-progress 1

# отметить как выполненную
python task_cli.py mark-done 1

# вывести только выполненные
python task_cli.py list done

# удалить задачу
python task_cli.py delete 1
