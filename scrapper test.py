import requests
#import pprint
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
import re

def web_scrapper_book(urls, num_book_per_page=40, max_num_pages=5):
    # HEADERS = ({'User-Agent':
    #                 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
    #             'Accept-Language': 'en-US, en;q=0.5'})

    HEADERS = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }

    Book = []
    for i in range(len(urls)):
        URL = urls.iloc[i, 1]
        page = requests.get(URL, headers=HEADERS)
        soup = BeautifulSoup(page.text, 'html.parser')
        res = soup.find('ul', class_='pagination search-pagination')
        if res:
            pages_available = \
            [''.join(re.findall('\d+', i.text)) for i in res.find_all('a') if bool(re.search('\d+', i.text))][-1]
        else:
            pages_available = 1
        num_pages = min(int(pages_available), max_num_pages)
        print('Start extracting ' + str(i+1) + ' subject: ' + urls.iloc[i, 0] + ' with ' + str(num_pages) + ' pages')

        for j in range(num_pages):
            URL_FULL = URL + '?Nrpp=' + str(num_book_per_page) + '&page=' + str(j + 1)
            page = requests.get(URL_FULL, headers=HEADERS)
            soup = BeautifulSoup(page.text, 'html.parser')
            results = soup.findAll('div', class_='product-shelf-tile product-shelf-tile-book bnBadgeHere columns-4')

            for book in results:
                title = book.find('a')['title']
                author = book.find_all('div', class_='product-shelf-author pt-0')
                if author:
                    author = author[0].find('a').text
                else:
                    author = None
                url = 'https://www.barnesandnoble.com' + book.find('a')['href']
                cover_url = book.find('div', class_='product-shelf-image').find('img')['src']
                Book += [[urls.iloc[i, 0], title, author, url, cover_url]]
    Book = pd.DataFrame(Book, columns=['Subject', 'Title', 'Author', 'Url', 'Cover_url'])
    return Book


def web_scrapper_overview(Book, from_, to_):

    if 'Overview' not in Book.columns:
        Book['Price'] = None
        Book['ISBN-10'] = None
        Book['ISBN-13'] = None
        Book['PubDate'] = None
        Book['Publisher'] = None
        Book['Overview'] = None

    # for i in range(len(Book)):
    for i in range(from_, to_):
        sleep(1)
        # HEADERS = ({'User-Agent':
        #                 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
        #             'Accept-Language': 'en-US, en;q=0.5'})
        HEADERS = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
        }

        url = Book.Url[i]
        print(i, url)
        page = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(page.text, 'html.parser')
        price = soup.find_all('span', class_ = 'price current-price ml-0')
        if price:
            price = float((price[0].text)[1:].replace(',', ''))

        book_info = soup.find_all('dd', class_='mb-xxs')
        book_info = [i.text for i in book_info]
        if book_info:
            Book.loc[i,'ISBN-10'] = book_info[0]
            Book.loc[i,'ISBN-13'] = book_info[1]
            Book.loc[i,'PubDate'] = book_info[2]
            Book.loc[i,'Publisher'] = book_info[3]
        elif not soup.find('table', class_='plain centered'):
            continue
        else:
            temp_info = [string for string in soup.find('table', class_='plain centered').stripped_strings]
            Book.loc[i,'ISBN-13'] = temp_info[1]
            Book.loc[i,'PubDate'] = temp_info[3]
            Book.loc[i,'Publisher'] = temp_info[5]
        Book.loc[i,'Price'] = price
        t = soup.find('div', {'class': 'text--medium overview-content bookseller-cont'})
        if t:
            p = t.find_all('p')
            if p:
                p = [i.text for i in p]
                p = ' '.join(p)
                Book.loc[i,'Overview'] = p
            else:
                component = []
                for string in t.stripped_strings:
                    component += [(string)]
                component = ' '.join(component)
                Book.loc[i,'Overview'] = component

    return Book


def ExtractBook(book_urls, num_book_per_page = 40, max_num_pages = 10):
    print('Start Scrapping Book...')
    books = web_scrapper_book(book_urls, num_book_per_page, max_num_pages)
    print('Start Scrapping Book Overviews...')
    final_books = web_scrapper_overview(books)
    return final_books


book_urls = pd.read_csv('../NLP-group-project/Subject_Url.csv')
book_urls = book_urls[120:160]

file_name = 'Book_121_160_subjects'

# Book_data = web_scrapper_book(book_urls, num_book_per_page = 40, max_num_pages = 30)


# new_Book = new_Book.drop_duplicates(subset = ['Title'])
# Book_data.to_csv(file_name + '.txt', sep = ',', index = False)
# print('Done Extracting '+ str(len(Book_data)) + ' Book Info...')
#
# #15924
# file_name = 'Book_1_40_subjects2'
new_Book = pd.read_csv(file_name + '.txt')

# drop duplicates

print('Starting Extracting '+ str(len(new_Book)) + ' Book Details...')

num_books = 200
if 'start_point' not in new_Book.columns:
    new_Book['start_point'] = 0
    print('start scraping from 0')
else:
    print('start scraping from ', new_Book['start_point'][0]*num_books)


if len(new_Book) % num_books == 0:
    end_point = int(len(new_Book) / num_books)
else:
    end_point = int(len(new_Book) / num_books) + 1

for i in range(new_Book['start_point'][0], end_point):
    start_index = i * num_books
    if len(new_Book) < (i+1)*num_books:
        end_index = len(new_Book)
    else:
        end_index = (i+1)*num_books
    print('Processed ' + str(start_index) + ' Books...')
    new_Book = web_scrapper_overview(new_Book, start_index, end_index)
    new_Book['start_point'] = i+1
    new_Book.to_csv(file_name+'.txt', sep=',', index=False)
    sleep(60)

# drop count column
new_Book = new_Book.drop(['start_point'], axis = 1)
# drop duplicates
# new_Book = new_Book.drop_duplicates(subset = ['Title'])


new_Book.to_csv(file_name + '.txt')