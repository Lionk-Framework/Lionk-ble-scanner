FROM python:3.13.3 

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache/pip

WORKDIR /app
COPY scanner.py /app

CMD ["python", "scanner.py"]
