import requests
import pprint
from bs4 import BeautifulSoup
import pandas as pd

url='https://www.barnesandnoble.com/b/textbooks/_/N-8q9'
headers= {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
}
req=requests.get(url,headers=headers)
soup=BeautifulSoup(req.content,'html.parser')
#sub1=soup.find('ul',attrs={'class':"lists lists--unstyled"},id="sidebar-section-TextbooksbySubject")
sub=soup.find_all('ul',attrs={'class':"lists lists--unstyled"})


full_urls=[]
num=len(sub)

# time complexity O(n)*O(m)
for i in range(num):
    if i is 0:
        continue
    for s in sub[i].find_all('a'):
        name=s.text
        Url='https://www.barnesandnoble.com/'+s.get('href')
        full_urls.append([name,Url])

Full_urls=[]
for subj,Url in full_urls:
    #print(subj)
    if subj is full_urls[-1][0] or subj is full_urls[1][0] or subj is full_urls[6][0]:
        Full_urls.append([subj,Url])
        print(subj)
        continue
    req=requests.get(Url,headers=headers)
    soup=BeautifulSoup(req.content,'html.parser')
    sub=soup.find_all('ul',attrs={'class':"lists lists--unstyled"},id="sidebar-section-0")[0]
    for s in sub.find_all('a'):
        name=s.text
        print(name)
        uurl='https://www.barnesandnoble.com/'+s.get('href')
        Full_urls.append([name,uurl])
book=pd.DataFrame(Full_urls,columns=['Subject','Url'])
book.to_csv('Subject_Url.csv', sep = ',', index = False)