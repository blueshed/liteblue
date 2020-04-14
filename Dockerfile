FROM python:3-slim
RUN apt-get update && apt-get install -y git
RUN pip install --upgrade pip
RUN pip install invoke alembic sqlalchemy pymysql aioredis tornado

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./liteblue /app/liteblue
COPY ./tests/app /app/app

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV PYTHONPATH ".:${PYTHONPATH}"
ENV PORT 80