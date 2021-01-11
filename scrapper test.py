import requests
import pprint
from bs4 import BeautifulSoup
import pandas as pd

book_urls = pd.read_csv('book_urls.txt')


def web_scrapper_book(urls, num_book_per_page=40, num_pages=5):
    HEADERS = ({'User-Agent':
                    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
                'Accept-Language': 'en-US, en;q=0.5'})

    Book = []
    for i in range(len(urls)):
        print('Start extracting subject: ' + urls.iloc[i, 0])
        URL = urls.iloc[i, 1]

        for j in range(num_pages):
            URL_FULL = URL + '?Nrpp=' + str(num_book_per_page) + '&page=' + str(j + 1)
            page = requests.get(URL_FULL, headers=HEADERS)
            soup = BeautifulSoup(page.text, 'html.parser')
            results = soup.findAll('div', class_='product-shelf-tile product-shelf-tile-book bnBadgeHere columns-4')

            for book in results:
                title = book.find('a')['title']
                author = book.find('div', class_='product-shelf-author pt-0').find('a').text
                url = 'https://www.barnesandnoble.com' + book.find('a')['href']
                cover_url = book.find('div', class_='product-shelf-image').find('img')['src']
                Book += [[urls.iloc[i, 0], title, author, url, cover_url]]
    Book = pd.DataFrame(Book, columns=['Subject', 'Title', 'Author', 'Url', 'Cover_url'])
    return Book


def web_scrapper_overview(Book, from_, to_):
    HEADERS = ({'User-Agent':
                    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
                'Accept-Language': 'en-US, en;q=0.5'})

    if 'Overview' not in Book.columns:
        Book['Price'] = None
        Book['ISBN-10'] = None
        Book['ISBN-13'] = None
        Book['PubDate'] = None
        Book['Publisher'] = None
        Book['Overview'] = None

    # for i in range(len(Book)):
    for i in range(from_ - 1, to_):
        if (i + 1) % 200 == 0:
            print('Processed ' + str(i + 1) + ' Books...')
        url = Book.Url[i]
        # print(i, url)
        page = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(page.text, 'html.parser')
        # price = soup.find('span', class_ = 'price current-price ml-0')
        # if price:
        # price = float((price.text)[1:].replace(',', ''))

        book_info = soup.find_all('dd', class_='mb-xxs')
        book_info = [i.text for i in book_info]
        if book_info:
            Book['ISBN-10'][i] = book_info[0]
            Book['ISBN-13'][i] = book_info[1]
            Book['PubDate'][i] = book_info[2]
            Book['Publisher'][i] = book_info[3]
        else:
            temp_info = [string for string in soup.find('table', class_='plain centered').stripped_strings]
            Book['ISBN-13'][i] = temp_info[0]
            Book['PubDate'][i] = temp_info[1]
            Book['Publisher'][i] = temp_info[2]
        # Book.Price[i] = price
        t = soup.find('div', {'class': 'text--medium overview-content bookseller-cont'})
        if t:
            p = t.find_all('p')
            if p:
                p = [i.text for i in p]
                p = ' '.join(p)
                Book.Overview[i] = p
            else:
                component = []
                for string in t.stripped_strings:
                    component += [(string)]
                component = ' '.join(component)
                Book.Overview[i] = component
    return Book


def ExtractBook(book_urls, num_book_per_page = 40, num_pages = 10):
    print('Start Scrapping Book...')
    books = web_scrapper_book(book_urls, num_book_per_page, num_pages)
    print('Start Scrapping Book Overviews...')
    final_books = web_scrapper_overview(books)
    return final_books


Book_data = web_scrapper_book(book_urls, num_book_per_page = 40, num_pages = 20)
new_Book = Book_data
for i in range(int(len(Book_data)/400)):
    new_Book = web_scrapper_overview(new_Book, i*400, (i+1)*400)

new_Book.to_csv('Book_5600.txt', sep = ',', index = False)
