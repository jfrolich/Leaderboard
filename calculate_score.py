import csv
import os

PATH = os.path.dirname(__file__)

REFERENCE_FILE = os.path.join(PATH, 'reuters_test.csv')

def create_csv_file():
    INFILE = 'c:\\Users\\JFrolich\\Documents\\Data sets\\Reuters\\fetch\\full_dataset\\metadata.csv'
    OUTFILE = 'reuters.csv'
    with open(INFILE, 'rb') as in_file:
        with open(OUTFILE, 'wb') as out_file:
            in_reader = csv.reader(in_file)
            in_reader.next()
            out_writer = csv.writer(out_file)
            out_writer.writerow(['id', 'acq'])

            for row in in_reader:
                # leave the last 3000 rows empty
                if int(row[0]) > 15668:
                    row[3] = ""
                out_writer.writerow([row[0], row[3]])

def read_reference_file():
    with open(REFERENCE_FILE, 'rb') as f:
        r = csv.reader(f)
        r.next()
        return { int(row[0]): int(row[1]) for row in r }

reference = read_reference_file()

class Error(Exception):
    pass

class IDNotFoundError(Error):
    pass

class WrongLabelError(Error):
    value = "Wrong label used in supplied file"

class DuplicateIDError(Error):
    value = "Duplicate ID found in file"

def calculate_score(file):
    with(open(file, 'rb')) as f:
        r = csv.reader(f)
        r.next()
        score = 0
        ids = set([])
        prediction = { int(row[0]): int(row[1] or 0) for row in r }
        for id, label in reference.items():
            if id in prediction:
                if   label == 1 and prediction[id] == 1:
                    # TP
                    score += 1
                elif label == 0 and prediction[id] == 1:
                    # FP
                    score -= 2
                elif label == 0 and prediction[id] == 0:
                    # TN
                    score += 1
                elif label == 1 and prediction[id] == 0:
                    # FN
                    score -= 5
                else:
                    raise WrongLabelError
            else:
                # the id in the prediction is not found in the reference set
                pass
                #raise IDNotFoundError
    return score

# print calculate_score('reuters.csv')
