from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.feature_selection import SelectKBest, chi2
import pandas as pd
import numpy as np
import os
import Orange

PATH = 'C:\\Challenge'

# Read metadata: labels
metadata = pd.read_table(os.path.join(PATH, 'reuters.csv'), sep=',')
y = metadata.acq

train = np.array([True if lab in [0,1] else False for lab in y])
test = np.array([False if lab in [0,1] else True for lab in y])

# Read text files in array
content = [open(os.path.join(PATH, 'text', str(f))).read() for f in metadata.id]

# Go from text to document-term-matrix ('vectorize' data)
vectorizer = CountVectorizer(decode_error = 'ignore')
X = vectorizer.fit_transform(content)

# Select the 100 best features
select = SelectKBest(chi2, k=50)
select.fit(X[train,:], y[train])

# Xs = matrix with the 100 selected features
Xs = select.transform(X)

# Weigthing the matrix
Xw = TfidfTransformer().fit_transform(Xs)
Xw = Xw.toarray()
# Extract feature names
feature_names = np.array(vectorizer.get_feature_names())[select.get_support()]

# Build orange data table, this is not really easy
features = [Orange.feature.Continuous(x) for x in [str(b) for b in list(feature_names)]]
classes = Orange.feature.Discrete("class", values=['0', '1'])
domain = Orange.data.Domain(features, classes, id)
feat_list = []
for i in range(Xw.shape[0]):
    feat_list.append(list(Xw[i,:]) + [int(y[i]) if y[i] < 3 else None])
out_data = Orange.data.Table(domain, feat_list)


id = Orange.feature.Descriptor.new_meta_id()

id_f = Orange.feature.String("id")
out_data.domain.addmeta(id, id_f)

for i, inst in enumerate(out_data):
    inst[id] = str(metadata.id[i])

#text = Orange.feature.Descriptor.new_meta_id()
#text_f = Orange.feature.String("text")
#out_data.domain.addmeta(text, text_f)

#for i, inst in enumerate(out_data):
#    inst[text] = str(content[i])

out_data.save(os.path.join(PATH, 'output_50.tab'))
