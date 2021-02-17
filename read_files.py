

import os
import pandas as pd

files = os.listdir()
file_names = [i for i in files if bool(re.search("book[0-9]*.txt", i))]
data = pd.concat(map(pd.read_csv, file_names))
data = data.drop_duplicates(['Title'])
data = data.reset_index().drop(['index'], axis = 1)

print(f'Total {len(data)} numbers of books')
print('Writing to txt file...')
data.to_csv('final_data.txt')