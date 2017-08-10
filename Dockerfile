FROM python:3.6

ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY skilled_hammer/ skilled_hammer/
COPY wsgi.py wsgi.py

EXPOSE 8000

CMD ["gunicorn", "-b", "0.0.0.0:8000", "-w", "4", "--access-logfile", "-", "wsgi:app"]
