source venv/bin/activate
cd tests
PYTHONPATH='..' python -m unittest -v
cd ..
python -m app