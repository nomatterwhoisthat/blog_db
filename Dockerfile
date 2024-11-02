# Используем официальный Python образ как базовый
FROM python:3.12-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл requirements.txt в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install alembic
#RUN pip install psycopg2-binary
# Копируем всё содержимое директории в рабочую директорию контейнера
COPY . .

# RUN alembic upgrade head

# Открываем порт 8000 для приложения
EXPOSE 8000

# Команда для запуска приложения с Uvicorn
CMD ["uvicorn", "blog.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
