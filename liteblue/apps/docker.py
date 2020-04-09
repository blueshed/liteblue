""" task to create Dockerfile and docker-compose.yml """
import os
import logging
from invoke import task

LOGGER = logging.getLogger(__name__)


@task
def docker(_, name, force=False):
    """ create a config folder with dev, staging & prod yamls """
    docker_file = "Dockerfile"
    LOGGER.info("gen docker: Dockerfile")
    if os.path.isfile(docker_file) and force is False:
        print("that file already exists: ", docker_file)
    else:
        with open(docker_file, "w") as file:
            file.write(
                """# Use an official Python runtime as a parent image
FROM python:3-slim
RUN apt-get update && apt-get install -y git

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# upgrade pip to make sure it can use git repos
RUN pip install --upgrade pip
RUN pip install liteblue

# Install any needed packages
RUN [ -f requirements.txt ] && pip install -r requirements.txt ||  echo "No requirements.txt"

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV PYTHONPATH ".:${PYTHONPATH}"
ENV PORT 80

"""
            )
        LOGGER.info("gen docker:docker-compose.yml")
        with open("docker-compose.yml", "w") as file:
            file.write(
                f"""version: '3'
services:
  web:
    build: .
    volumes:
        - .:/app
    image: {name}:latest
    container_name: {name}-web
    command: liteblue run {name}
    ports:
      - "8080:80"
"""
            )
