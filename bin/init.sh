python3.7 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp ./app/alembic.ini.dist ./app/alembic.ini
cp ./config/config.yaml.dist ./config/config.yaml
python init_db.py
cd app
PYTHONPATH='..' alembic revision --autogenerate -m "Init user table"
PYTHONPATH='..' alembic upgrade head
cd ../tests
PYTHONPATH='..' python -m unittest
