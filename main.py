import csv

import requests
from bs4 import BeautifulSoup


def get_term():
    with open('term.txt', 'r') as file:
        return file.readline()


book_cache = {}


def get_books_for_course(dept, num, sect):
    key = str(dept) + "-" + str(num) + "-" + str(sect)
    if key in book_cache:
        return book_cache[key]

    term = get_term()

    headers = {
        'User-Agent': 'AggieShieldsLookupBot/1.0',
    }

    post_data = "<?xml version='1.0' encoding='UTF-8'?><textbookorder><courses>"
    # The following line can be repeated multiple times to lookup multiple courses
    post_data += "<course dept='" + str(dept) + "' num='" + str(num) + "' sect='" + str(
        sect) + "' term='" + term + "'/>"
    post_data += "</courses></textbookorder>"

    response = requests.post('http://tamu.bncollege.com/webapp/wcs/stores/servlet/TBListView',
                             headers=headers,
                             data={
                                 'TS015810ea_id': '1',  # magic number that makes the form work
                                 'courseXml': post_data,
                                 'storeId': '17552',  # Use the TAMU bookstore
                             })
    soup = BeautifulSoup(response.content, 'lxml')

    for course_dom in soup.select('div.book_sec'):
        course_header = course_dom.select('div.courseOverView_panel.padding_TBList > h1')[0]
        dept, num = course_header.contents[1].text.split(' ')
        sect = course_header.contents[2].strip()
        dom_key = str(dept) + "-" + str(num) + "-" + str(sect)
        books = course_dom.select('div.book-list div.book_desc1.cm_tb_bookInfo')
        book_dict_list = []
        for book_dom in books:
            book_dict = {
                "title": book_dom.select('a')[0].get('title'),
                "author": book_dom.select('h2 span i')[0].text[3:],
                "edition": book_dom.select('li.book_c1')[0].text.strip()[8:].strip(),
                "isbn": book_dom.select('li.book_c2_180616')[0].text[6:].strip(),
                "required": book_dom.select('h2 span.recommendBookType')[0].text.strip() == 'REQUIRED'
            }
            book_dict_list.append(book_dict)
        book_cache[dom_key] = book_dict_list
        return book_dict_list


def print_books_for_course(dept, num, sect):
    book_dict_list = get_books_for_course(dept, num, sect)
    print('************************* ' + dept + '-' + str(num) + '-' + str(sect) + ' *************************')

    for book in book_dict_list:
        print()  # force a new line
        print(book['title'] + ' (' + book['edition'] + ' edition)')
        print(' - by ' + book['author'])
        print(' - ISBN: ' + book['isbn'])
        print(' - Required: ' + str(book['required']))


if __name__ == '__main__':
    all_books = []

    with open('courses.csv', 'r') as file:
        course_reader = csv.reader(file)
        for dept, num, sect in course_reader:
            if dept == "DEPARTMENT" or num == "NUMBER" or sect == "SECTION":
                continue
            book_list_dict = get_books_for_course(dept, num, sect)
            all_books.extend(book_list_dict)

    with open('books.csv', 'w') as file:
        book_writer = csv.writer(file)
        book_writer.writerow(['TITLE', 'AUTHOR', 'EDITION', 'ISBN', 'REQUIRED'])
        for book in all_books:
            book_writer.writerow([book['title'], book['author'], book['edition'], book['isbn'], str(book['required'])])
