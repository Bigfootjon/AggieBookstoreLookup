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
        'User-Agent': 'AggieBookstoreLookupBot/1.0',
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
        books = course_dom.select('div.book-list')
        book_dict_list = []
        for book_dom in books:
            book_dict = {
                "title": book_dom.select('h1 a')[0].get('title'),
                "author": book_dom.select('h2 span i')[0].text[3:],
                "edition": book_dom.select('li.book_c1')[0].text.strip()[8:].strip(),
                "isbn": book_dom.select('li.book_c2_180616')[0].text[6:].strip(),
                "required": book_dom.select('h2 span.recommendBookType')[0].text.strip() == 'REQUIRED',
                "price": [price.select("span")[0].text.strip()[1:] for price in book_dom.select('ul ul.cm_tb_bookList li.selectableBook') if price['title'] == "BUY NEW "][0]
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
        print(' - Price: ' + book['price'])


def get_all_courses(filename):
    all_courses = []

    with open(filename, 'r') as file:
        course_reader = csv.reader(file)
        for dept, num, sect in course_reader:
            if dept == "DEPARTMENT" or num == "NUMBER" or sect == "SECTION":
                continue
            all_courses.append(get_books_for_course(dept, num, sect))

    all_courses.sort(key=lambda o: len(o), reverse=True)

    return all_courses


def write_all_books(filename, all_courses):
    with open(filename, 'w') as file:
        rows = []

        for course in all_courses:
            for i, book in enumerate(course):
                if i >= len(rows):
                    rows.append([book])
                else:
                    rows[i].append(book)

        header = []
        for _ in range(len(rows[0])):
            header.extend(["TITLE", "AUTHOR", "EDITION", "ISBN", "REQUIRED", "PRICE"])

        book_writer = csv.writer(file)
        book_writer.writerow(header)

        for row in rows:
            csv_row = []
            for book in row:
                csv_row.extend([book['title'], book['author'], book['edition'], book['isbn'], str(book['required']), book['price']])
            book_writer.writerow(csv_row)


if __name__ == '__main__':
    all_books = get_all_courses('courses.csv')
    write_all_books('books.csv', all_books)
