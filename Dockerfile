FROM python:3.12

ENV PYTHONPATH=/srv \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /srv/

COPY requirements.txt /srv/
RUN python3.12 -m pip install --no-cache-dir -r requirements.txt

COPY . /srv/

CMD ["python3.12", "src/app.py"]
