# 1. Base image for Python 3.10.11
FROM python:3.10.11-slim

# 2. Set working directory
WORKDIR /code

# 3. Optimize builds by installing dependencies first
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# 4. Copy all project files (including src/ and external files)
COPY . .

# 5. Set PYTHONPATH to include the current directory
# This allows Python to recognize "src" as a package
ENV PYTHONPATH=/code

# 6. Run the app using the package:instance format
# Since the app instance is in __init__.py, you refer to the directory name
CMD ["uvicorn", "src:app", "--host", "0.0.0.0", "--port", "80"]
