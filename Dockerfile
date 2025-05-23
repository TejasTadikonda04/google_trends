# Dockerfile for Streamlit Dashboard

# Base image
FROM python:3.10

# Set UTF-8 locale
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose default Streamlit port
EXPOSE 8501

# Run the app
CMD ["sh", "-c", "python transform.py && python load.py && streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0"]
