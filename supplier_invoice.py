import json
import requests
import argparse
import csv
import sys
import time
import jsonschema
from jsonschema import validate

# const
URL = 'https://api.fortnox.se/3/supplierinvoices/'
JSON_SCHEMA_FILE = 'supplier_invoice_schema.json'

# init params
parser = argparse.ArgumentParser(description='Create supplier invoice.')
parser.add_argument('--file',
                    metavar='FILE',
                    dest='CSV_FILE',
                    action='store',
                    required=True,
                    help='csv file (default: supplier_invoice.csv)')
parser.add_argument('--access_token',
                    metavar='ACCESS_TOKEN',
                    dest='ACCESS_TOKEN',
                    action='store',
                    required=True,
                    help='rest api access token')
parser.add_argument('--client_secret',
                    metavar='CLIENT_SECRET',
                    action='store',
                    dest='CLIENT_SECRET',
                    required=True,
                    help='rest api client secret')
parser.add_argument('--dry_run',
                    metavar='DRY_RUN',
                    default=True,
                    dest='DRY_RUN',
                    type=lambda x: (str(x).lower() == 'true'),
                    help='whether or not call http endpoint')
args = parser.parse_args()
marsked_access_token = args.ACCESS_TOKEN[:4] + \
    args.ACCESS_TOKEN[-4:].rjust(len(args.ACCESS_TOKEN) - 4, "*")
marsked_client_secret = args.CLIENT_SECRET[:4] + \
    args.CLIENT_SECRET[-2:].rjust(len(args.CLIENT_SECRET) - 2, '*')
print('\r\nProcessing csv file: ' + args.CSV_FILE + ' with ACCESS_TOKEN: <' +
      marsked_access_token + '> and CLIENT_SECRET: <' + marsked_client_secret + '>')
time.sleep(.5)

# read json schema
print('\r\nReading json schema ...')
with open(JSON_SCHEMA_FILE) as jsonSchemaFile:
    jsonSchema = json.load(jsonSchemaFile)
    print('Successfully load schema file')
time.sleep(.5)

# read csv data
print('\r\nReading supplier invoice from csv file ...')
invoices = []
with open(args.CSV_FILE) as csvfile:
    csvData = csv.reader(csvfile, delimiter=';')
    iterCsvData = iter(csvData)
    next(iterCsvData)
    for index, row in enumerate(csvData):
        invoice = {}

        i = {}
        i['SupplierNumber'] = row[0]
        i['Total'] = float(row[3].replace(',', '').replace(' ', ''))
        i['VAT'] = float(row[4].replace(',', '').replace(' ', ''))
        i['VATType'] = row[9].upper()
        i['SalesType'] = 'SERVICE'.upper()  # TODO?
        i['Currency'] = 'SEK'
        i['CurrencyRate'] = "1"
        i['CurrencyUnit'] = 1
        i['DueDate'] = row[2]
        i['InvoiceDate'] = row[1]

        i['SupplierInvoiceRows'] = []
        supplierInvoiceRow1 = {}
        supplierInvoiceRow1['Account'] = int(row[10])
        supplierInvoiceRow1['Debit'] = float(0)
        supplierInvoiceRow1['Credit'] = float(row[11].replace(',', '').replace(' ', ''))
        supplierInvoiceRow1['Total'] = float(row[11].replace(',', '').replace(' ', ''))
        i['SupplierInvoiceRows'].append(supplierInvoiceRow1)

        supplierInvoiceRow2 = {}
        supplierInvoiceRow2['Account'] = int(row[12])
        supplierInvoiceRow2['Debit'] = float(0)
        supplierInvoiceRow2['Credit'] = float(row[13].replace(',', '').replace(' ', ''))
        supplierInvoiceRow2['Total'] = float(row[13].replace(',', '').replace(' ', ''))
        i['SupplierInvoiceRows'].append(supplierInvoiceRow2)

        supplierInvoiceRow3 = {}
        supplierInvoiceRow3['Account'] = int(row[14])
        supplierInvoiceRow3['Debit'] = float(0)
        supplierInvoiceRow3['Credit'] = float(row[15].replace(',', '').replace(' ', ''))
        supplierInvoiceRow3['Total'] = float(row[15].replace(',', '').replace(' ', ''))
        i['SupplierInvoiceRows'].append(supplierInvoiceRow3)

        supplierInvoiceRow4 = {}
        supplierInvoiceRow4['Account'] = int(row[16])
        supplierInvoiceRow4['Credit'] = float(0)
        supplierInvoiceRow4['Debit'] = float(row[17].replace(',', '').replace(' ', ''))
        supplierInvoiceRow4['Total'] = float(row[17].replace(',', '').replace(' ', ''))
        i['SupplierInvoiceRows'].append(supplierInvoiceRow4)

        invoice['SupplierInvoice'] = i

        try:
            validate(instance=invoice, schema=jsonSchema)
        except jsonschema.ValidationError as e:
            print('Invalid line: ' + str(index + 2) + ' in csv file: ' + args.CSV_FILE)
            print('Error cause: ' + e.message + '\r\n')
            sys.exit(1)

        if args.DRY_RUN:
            print('\r\nDry run mode enabled, printing invoice from supplier: ' + str(invoice['SupplierInvoice']['SupplierNumber']))
            print(json.dumps(invoice, indent=2, sort_keys=True))

        invoices.append(invoice)
print('Successfully loaded ' + str(len(invoices)) + ' invoices from csv file')
time.sleep(.5)

# create supplier invoices
headers = {
    'Access-Token': args.ACCESS_TOKEN,
    'Client-Secret': args.CLIENT_SECRET,
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

if not args.DRY_RUN:
    success = 0
    failure = 0
    for i in invoices:
        supplierNumber = i['SupplierInvoice']['SupplierNumber']
        print('\r\nCreating invoice for Supplier with supplier number: ' + supplierNumber, end = ' ')

        for j in range(5):
            time.sleep(.25)
            sys.stdout.write('.')
            sys.stdout.flush()

        # debug line, enable to verify payload
        # print(json.dumps(i, indent=4, sort_keys=True))

        sys.stdout.write('\r\n')
        sys.stdout.flush()
        res = requests.post(url = URL, data = json.dumps(i), headers = headers)
        if res.status_code == 201:
            success += 1
            print('Successfully to create invoice for supplier: ' + supplierNumber)
        else:
            failure += 1
            print('Failed to create invoice for supplier: ' + supplierNumber)
            print('Failure status code: ' + str(res.status_code))
            print('Failure reason: ' + str(res.content))
        time.sleep(.5)

    # summary
    print('\r\nFinal result:')
    print('Total processed: ' + str(len(invoices)) + ', success: ' + str(success) + ', failure: ' + str(failure))
    time.sleep(.5)
else:
    print('\r\nDry run mode enable, skip and continue. To abort dry run mode, run with --dry_run False')
    time.sleep(2)
