FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY Pipfile Pipfile.lock /app/

RUN pip install --no-cache-dir pipenv

RUN pipenv install --system --deploy

COPY . /app/

EXPOSE 8000

CMD ["python", "main.py"]
