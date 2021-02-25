import json
from sentence_transformers import SentenceTransformer, CrossEncoder, util
import time
import gzip
import os
import pandas as pd
import torch


# bi-encoder
model=SentenceTransformer('msmarco-distilbert-base-v2')
top_k=20

# cross-encoder to improve quality
cross_encoder=CrossEncoder('cross-encoder/ms-marco-TinyBERT-L-6')


# load database
#database=pd.read_csv('Book_5600.csv')
database=pd.read_csv('final_data.txt',sep=',')
database.columns=['Subject', 'Title', 'Author', 'Url', 'Cover_url','Price','ISBN-10','ISBN-13','PubDate','Publisher','Overview']
overview=[x for x in database['Overview'] if not pd.isnull(x)]
title=[database['Title'][i] for i in range(len(database['Title'])) if not pd.isnull(database['Overview'][i])]
subject=[database['Subject'][i] for i in range(len(database['Subject'])) if not pd.isnull(database['Overview'][i])]

# embedding for database (overview)
database_embedding=model.encode(overview,show_progress_bar=True)


que=input("please enter keywords :")

start_time=time.time()

# embedding for query
q_embedding=model.encode(que,convert_to_tensor=True)
res=util.semantic_search(q_embedding,database_embedding,top_k=top_k)[0]


# score all retrieved passage with the cross_encoder
cross_inp=[[que,overview[r['corpus_id']]] for r in res]
cross_sco=cross_encoder.predict(cross_inp)

# sort results by the cross-encoder score:
for idx in range(len(cross_sco)):
  res[idx]['cross_score']=cross_sco[idx]
  
res=sorted(res,key=lambda x:x['cross_score'],reverse=True)
end_time=time.time()

print("Input keywords:", que)
print("Results (after {:.3f} seconds):".format(end_time-start_time))
for r in res:
  print("\t{} \t{:.3f} \t{}".format(subject[r['corpus_id']],r['cross_score'],title[r['corpus_id']]))
