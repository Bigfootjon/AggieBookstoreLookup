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
        books = book_cache[key]
        for book in books:
            book['dept'] = dept
            book['num'] = num
        return books

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
                "price": [price.select("span")[0].text.strip()[1:] for price in
                          book_dom.select('ul ul.cm_tb_bookList li.selectableBook') if price['title'] == "BUY NEW "][0],
                "dept": dept,
                "num": num
            }
            book_dict_list.append(book_dict)
        book_cache[dom_key] = book_dict_list
        return book_dict_list


def get_all_courses(filename):
    all_courses = []

    with open(filename, 'r') as file:
        course_reader = csv.reader(file)
        for dept, num, sect in course_reader:
            if dept == "DEPARTMENT" or num == "NUMBER" or sect == "SECTION":
                continue
            all_courses.extend(get_books_for_course(dept, num, sect))

    return all_courses


def write_all_books(filename, users):
    csv_list = []

    header_template = ["Book Title", "Author", "Department", "Course", "ISBN", "Amount", "In Library"]

    for user in users:
        if len(csv_list) == 0:
            csv_list.append(header_template)
        else:
            csv_list[0].extend(header_template)
        for i, book in enumerate(user['books']):
            book_csv = [book['title'] + book['edition'], book['author'], book['dept'], book['num'], book['isbn'], book['price'], user['name']]
            if len(csv_list) <= i:
                csv_list.append(book_csv)
            else:
                csv_list[i].extend(book_csv)

    with open(filename, 'w') as file:
        book_writer = csv.writer(file)
        for csv_row in csv_list:
            book_writer.writerow(csv_row)


def get_all_csv_users():
    users = []
    file_name = 'input/courses.csv'
    users.append({
        "name": file_name,
        "books": get_all_courses(file_name)
    })

    users.sort(key=lambda o: len(o["books"]), reverse=True)

    return users


if __name__ == '__main__':
    users = get_all_csv_users()
    write_all_books('books.csv', users)
