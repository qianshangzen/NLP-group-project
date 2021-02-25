
import os
import pandas as pd
import itertools as it
import re

def customized_pd_read(file_path, hdr):
    print("Reading file " + file_path)
    return pd.read_csv(file_path, header = hdr)

files = os.listdir()
file_names = [i for i in files if bool(re.search("book[0-9]*.txt", i))]
data = pd.concat(it.starmap(customized_pd_read, list(map(lambda x: (x, None), file_names))))
print(f'Finished reading {len(data)} books')

data.columns = ['Subject','Title','Author','Url','Cover_url','Price','ISBN-10','ISBN-13','PubDate','Publisher','Overview']
data = data.drop_duplicates(['Title'])
data = data.reset_index().drop(['index'], axis = 1)
data.to_csv('final_data.txt', index = False)
print(f'After cleaning, total {len(data)} of books is saved to "final_data.txt"')
