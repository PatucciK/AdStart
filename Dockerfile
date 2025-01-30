# Используем официальный Python образ как базовый
FROM python:3.12-slim

# Установить зависимости системы
# Установить зависимости системы и локали
RUN apt-get update && apt-get install -y \
    git \
    locales \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Генерация локалей
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    echo "ru_RU.UTF-8 UTF-8" >> /etc/locale.gen && \
    locale-gen

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файлы зависимостей (requirements.txt) в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в контейнер
COPY . .

# Установить локаль по умолчанию
ENV LC_ALL=ru_RU.UTF-8
ENV LANG=ru_RU.UTF-8

# Запускаем команду для создания миграций (например, collectstatic, если нужно)
# RUN python manage.py migrate

# Открываем порт для приложения
EXPOSE 8000

ENTRYPOINT ["python", "manage.py", "runserver"]