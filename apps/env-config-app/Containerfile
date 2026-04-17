FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
ENV APP_NAME=env-config-app
ENV APP_ENV=production
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
