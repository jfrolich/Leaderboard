import random
with open('reuters.csv', 'rb') as f:
    with open('reuters_random.csv', 'wb') as fw:
        fw.write('id, label\n')
        for row in f:
            id, label = row.replace('\n', '').replace('\r', '').split(',')
            if label == '':
                fw.write('%s,%d\n' % (id, 1 if random.random() > 0.5 else 0))
