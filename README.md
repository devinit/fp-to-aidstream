# fp-to-aidstream
A test flask converter for FocalPoint XML output to AidStream template CSV

## To install:
```
python3 -m virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

## To run:
`python3 app.py`

## To bundle:
`pyinstaller -F --add-data "static;static" --add-data "templates;templates" app.py`
