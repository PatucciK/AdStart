# Используем официальный Python образ как базовый
FROM python:3.12-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файлы зависимостей (requirements.txt) в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в контейнер
COPY . .

# Запускаем команду для создания миграций (например, collectstatic, если нужно)

RUN python manage.py migrate

# Открываем порт для приложения
EXPOSE 8000

# Запускаем Django сервер на 0.0.0.0, чтобы было доступно снаружи
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
