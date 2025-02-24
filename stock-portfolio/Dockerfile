# Use a basic Python image
FROM python:3.9-slim

# Create a working directory inside the container where commands will run
WORKDIR /app

# Copy all files into the container
COPY . /app

# Set an environment variable for the API key
ENV NINJA_API_KEY="vopFoYntOSunu9wOgno8UQ==6N9s5bNi9ndGWM5I"

# Install dependencies from requirements.txt
RUN pip install -r requirements.txt

# Expose port 8000
EXPOSE 8000

# Run the application
CMD ["python", "app.py"]

# Set an environment variable for the port
ENV PORT=8000

