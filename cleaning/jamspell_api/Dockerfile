FROM python:3.10-slim

# Install system dependencies inkl. yacc (via bison!)
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    curl \
    unzip \
    git \
    automake \
    libtool \
    autoconf \
    bison \
    libboost-all-dev \
    libprotobuf-dev \
    protobuf-compiler \
    zlib1g-dev \
    libicu-dev \
    libpcre3-dev \
    pkg-config \
    locales && \
    rm -rf /var/lib/apt/lists/*

# Install SWIG 3.0.12
WORKDIR /tmp
RUN wget -q https://github.com/swig/swig/archive/refs/tags/rel-3.0.12.zip && \
    unzip rel-3.0.12.zip && \
    cd swig-rel-3.0.12 && \
    ./autogen.sh && \
    ./configure && \
    make && \
    make install && \
    cd / && rm -rf /tmp/*

# Set working dir
WORKDIR /app

# Copy project
COPY . .

# Python dependencies
RUN pip install --upgrade pip
RUN pip install flask jamspell
RUN pip install waitress
# Locale
RUN apt-get update && apt-get install -y locales && \
    sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen

ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8

# Expose port
EXPOSE 5000

# Run app
CMD ["python", "app.py"]
