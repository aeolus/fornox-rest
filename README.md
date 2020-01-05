### Install python and pip (recommended to run with python 3.7 or above)

#### Before started, copy csv file into the folder
```
$> cp ../sample.csv .
```

#### Install dependencies, need to run every time after update script
```
$> pip install -r requirements.txt
```

#### To get help:
```
$> python supplier_invoice.py -h
```

### To run with dry-run mode (no invoice will be created):
```
$> python supplier_invoice.py --file CSV_FILE --access_token ACCESS_TOKEN --client_secret CLIENT_SECRET
```
### To run:
```
$> python supplier_invoice.py --file CSV_FILE --access_token ACCESS_TOKEN --client_secret CLIENT_SECRET --dry_run False
```
