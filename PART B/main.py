import requests
from bs4 import BeautifulSoup
import sqlite3
import time


# Part B Functions

# Function to fetch and parse a page
def fetch_and_parse_page(url):
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.text, 'html.parser')
    else:
        print(f"Failed to fetch {url}")
        return None

# Function to scrape books data from a page
def scrape_books_data(page_url):
    soup = fetch_and_parse_page(page_url)
    if soup:
        books = soup.find_all('article', class_='product_pod')
        book_data = []
        for book in books:
            title = book.h3.a.attrs['title']
            price = book.find('p', class_='price_color').text
            availability = book.find('p', class_='instock availability').text.strip()
            rating = ' '.join(book.find('p', class_='star-rating').attrs['class'][-1:])
            book_data.append((title, price, availability, rating))
        return book_data
    else:
        return None

# Function to store books data in the database
def store_books_in_db(books, connection):
    cursor = connection.cursor()
    for book in books:
        cursor.execute("INSERT INTO books (title, price, availability, rating) VALUES (?, ?, ?, ?)", book)
    connection.commit()

# Function to write output for Part B
def write_output_part_b(books_data):
    with open("output_part_b.txt", "w", encoding="utf-8") as f:
        f.write("Books Data:\n")
        for book in books_data:
            f.write(f"Title: {book[0]}, Price: {book[1]}, Availability: {book[2]}, Rating: {book[3]}\n")

# Function to execute Part B
def execute_part_b():
    connection = sqlite3.connect("part_b.db")
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS books (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            title TEXT,
                            price TEXT,
                            availability TEXT,
                            rating TEXT
                        )''')
    base_url = "http://books.toscrape.com/catalogue/page-{}.html"
    books_data = []
    for page_number in range(1, 51):
        page_url = base_url.format(page_number)
        print(f"Scraping page {page_number}...")
        page_books_data = scrape_books_data(page_url)
        if page_books_data:
            store_books_in_db(page_books_data, connection)
            books_data.extend(page_books_data)
            print(f"Page {page_number} scraped and data stored successfully.")
        else:
            print(f"Failed to scrape page {page_number}.")
        # Add a delay to avoid overwhelming the server
        time.sleep(1)
    write_output_part_b(books_data)
    connection.close()


execute_part_b()
