# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10-slim

EXPOSE 8000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Copy local code to the container image.
WORKDIR /app
COPY . /app

# Install pip requirements
RUN pip3 install -r requirements.txt --no-cache-dir

# the actual python app is located in the movieRental folder
WORKDIR /app/movieRental

ENTRYPOINT ["python3"] 
CMD ["manage.py", "runserver", "0.0.0.0:8000"]