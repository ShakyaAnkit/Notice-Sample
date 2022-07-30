# Sample Project

## Project Setup
```bash
pip install -r requirements.txt
cp suchana_portal/settings.py.example suchana_portal/settings.py
python manage.py makemigrations dashboard home
python manage.py migrate
```

## Create superuser
```bash
python manage.py createsuperuser
```

## Create Elasticsearch index
```bash
python manage.py search_index --rebuild
```

## Additional Changes (2021-06-25)
```
pip install celery==4.4.2
pip install redis==3.5.3
```

On `settings.py`
```python
# Celery
CELERY_BROKER_URL = 'redis://localhost:6379'
```

### Run celery
Start celery worker
```bash
celery -A suchana_portal worker -l info
```

Start celery beat
```bash
celery -A suchana_portal beat -l info
```