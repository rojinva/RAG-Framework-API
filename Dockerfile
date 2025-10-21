FROM artifactory.lamresearch.com:443/lam-all-docker-lwestus/python/python:3.11.3


ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off

WORKDIR /app

# Upgrade pip first
RUN pip install --upgrade pip && pip install poetry && poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./

# Install dependencies and the ODBC driver
RUN poetry install --no-root --without testing && \
    apt-get update && \
    apt-get install -y curl apt-transport-https gnupg lsb-release && \
    curl https://packages.microsoft.com/keys/microsoft.asc | tee /etc/apt/trusted.gpg.d/microsoft.asc && \
    bash -c 'case $(lsb_release -rs) in \
        9) curl https://packages.microsoft.com/config/debian/9/prod.list | tee /etc/apt/sources.list.d/mssql-release.list ;; \
        10) curl https://packages.microsoft.com/config/debian/10/prod.list | tee /etc/apt/sources.list.d/mssql-release.list ;; \
        11) curl https://packages.microsoft.com/config/debian/11/prod.list | tee /etc/apt/sources.list.d/mssql-release.list ;; \
        12) curl https://packages.microsoft.com/config/debian/12/prod.list | tee /etc/apt/sources.list.d/mssql-release.list ;; \
        *) echo "Debian $(lsb_release -rs) is not currently supported."; exit 1 ;; \
    esac' && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17 && \
    ACCEPT_EULA=Y apt-get install -y mssql-tools && \
    echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc && \
    apt-get install -y unixodbc-dev && \
    apt-get install -y libgssapi-krb5-2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


COPY . .

RUN ls -l

# Expose the port on which the application will run
EXPOSE 8000

# Add certificate to env and run the FastAPI application using uvicorn server
CMD ["sh", "-c",  "cat /app/cacert_lam.pem >> /usr/local/lib/python3.11/site-packages/certifi/cacert.pem && gunicorn -k uvicorn.workers.UvicornWorker -w 2 --worker-connections 1000 -b 0.0.0.0:8000 --timeout 120 --max-requests 100 --max-requests-jitter 20 src.app:app"]