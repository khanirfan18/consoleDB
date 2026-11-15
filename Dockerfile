# 1. Base Image: Ek chhota aur fast Linux OS jisme Python 3.13 pehle se install ho
FROM python:3.13-slim

# 2. Environment Variables: Python ko thoda fast aur clean banate hain
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Work Directory: Docker ke dibbe ke andar hum ek '/app' naam ka folder bana rahe hain
WORKDIR /app

# 4. Requirements Copy: Sirf requirements file ko pehle dibbe mein daalo
COPY requirements.txt /app/

# 5. Install Packages: Saare packages install karo bina cache memory bhare
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy Project Code: Ab baaki ka poora Django code dibbe ke andar copy kar do
COPY . /app/

# 7. Port Expose: Docker dibbe ka port 8000 open kar do taaki bahar se traffic aa sake
EXPOSE 8000

# 8. Start Engine: Runserver ki jagah Gunicorn (Production Engine) se project start karo
CMD ["gunicorn", "consoledb.wsgi:application", "--bind", "0.0.0.0:8000"]