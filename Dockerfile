FROM python:3

EXPOSE 8000
VOLUME /var/lib/recipes

# Deploy the code and create the support folders
RUN useradd -m recipes -s /bin/bash -d /opt/recipes
RUN mkdir -p /opt/recipes /var/lib/recipes /var/www/recipes
RUN chown recipes:recipes /var/lib/recipes /var/www/recipes
COPY . /opt/recipes/
WORKDIR /opt/recipes

# Install requirements
RUN apt-get update \
 && apt-get upgrade -y \
 && apt-get install -y postgresql-client \
 && apt-get autoremove \
 && apt-get autoclean
RUN pip3 install --no-cache-dir psycopg2-binary gunicorn
RUN pip3 install --no-cache-dir -r requirements.txt

# Start server
USER recipes
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
CMD ["./run.sh"]
