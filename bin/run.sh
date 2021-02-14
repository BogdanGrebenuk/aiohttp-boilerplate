source venv/bin/activate
cd tests
PYTHONPATH='..' python -m unittest
cd ..
python -m app