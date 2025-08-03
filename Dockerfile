FROM python:3.12-slim

WORKDIR /app

# Install system dependencies first
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir  --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt

RUN python -c "import nltk; nltk.download('stopwords')"

EXPOSE 8501


# Starte mit Entpack-Check
CMD ["bash", "-c", "\
    if [ ! -f /app/data/reviews.csv ]; then \
        echo '📦 Entpacke ZIP-Dateien im gemounteten Datenverzeichnis ...'; \
        unzip -o /app/data/dataset.zip -d /app/data; \
        unzip -o /app/data/review_label.zip -d /app/data; \
        unzip -o /app/data/reviews_no_txt.zip -d /app/data; \
    else \
        echo '✅ CSV-Dateien vorhanden. Kein Entpacken nötig.'; \
    fi && \
    if [ ! -f /app/yelp.db ]; then \
        echo '📂 Entpacke yelp.zip in tmp und kopiere yelp.db ins Root ...'; \
        mkdir -p /app/tmp_unzip && \
        unzip -o /app/yelp.zip -d /app/tmp_unzip && \
        cp /app/tmp_unzip/yelp.db /app/yelp.db && rm -r /app/tmp_unzip; \
    else \
        echo '✅ yelp.db bereits vorhanden.'; \
    fi && \
    streamlit run app.py \
"]