FROM python:3.8.6-slim-buster

# set working directory in container
WORKDIR /usr/src/app

# set env variables
ENV PORT 8050

# Copy and install packages
COPY requirements.txt /
RUN pip install --upgrade pip
RUN pip install -r /requirements.txt

# Copy app folder to app folder in container
COPY /app /usr/src/app/

# Changing to non-root user
RUN useradd -m appUser
USER appUser

# Run locally on port 8050
CMD gunicorn --bind 0.0.0.0:$PORT index:server