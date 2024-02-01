# IMPORT LIBRARIES
import json
import requests
import sys

DATABASE_URLS = {
    0: 'https://library-one-default-rtdb.firebaseio.com/.json',
    1: 'https://library-two-9a851-default-rtdb.firebaseio.com/.json'
}


class BookLibrary:
    def __init__(self, capacity=7):

        self.capacity = capacity #set initial index size = 7
        self.firebase_odd = DATABASE_URLS[0]
        self.firebase_even = DATABASE_URLS[1]

    def polynomial_hash(self, author):
        
        hash_value = 0
        for char in author:
            hash_value = (hash_value * 37 + ord(char)) % self.capacity #polynomial hashing
        return hash_value

    def insert(self, book_id, author, title, year, price):

        hash_value = self.polynomial_hash(author)
        book = {book_id: {"author": author, "title": title, "year": year, "price": price}}

        try:
            if hash_value % 2 == 0:
                response = requests.patch(self.firebase_even, json.dumps(book), timeout=10)
            else:
                response = requests.patch(self.firebase_odd, json.dumps(book), timeout=10)

            return response.status_code
        
        except requests.ConnectionError:
            print("Connection error occurred")
            return "Error"  
        except requests.Timeout:
            print("Timeout occurred")
            return "Error"  


library = BookLibrary()
#----------------------------------------------------------

def add_book(book_id, book_json):

    # INPUT : book id and book json from command line
    # RETURN : status code after pyhton REST call to add book [response.status_code]
    # EXPECTED RETURN : 200

    data = json.loads(book_json)

    author = data["author"]
    price = data["price"]
    title = data["title"]
    year = data["year"]

    status_code = library.insert(book_id, author, title, year, price)

    return status_code

def search_by_author(author_name):
    # INPUT: Name of the author
    # RETURN: JSON object having book_ids as keys and book information as value [book_json] published by that author  
    # EXPECTED RETURN TYPE: {'102': {'author': ... , 'price': ..., 'title': ..., 'year': ...}, '104': {'author': , 'price': , 'title': , 'year': }}
    
    hash_value = library.polynomial_hash(author_name)
    
    if hash_value % 2 == 0:
        #read even
        query_url = f'{library.firebase_even}?orderBy="author"&equalTo="{author_name}"'
        response = requests.get(query_url)
        data = response.json()
        return json.dumps(data)
    
    else:
        #read odd
        query_url = f'{library.firebase_odd}?orderBy="author"&equalTo="{author_name}"'
        response = requests.get(query_url)
        data = response.json()
        return json.dumps(data)


def search_by_year(year):

    # INPUT: Year when the book published
    # RETURN: JSON object having book_ids as key and book information as value [book_json] published in that year
    # EXPECTED RETURN TYPE: {'102': {'author': ... , 'price': ..., 'title': ..., 'year': ...}, '104': {'author': , 'price': , 'title': , 'year': }}

    combined_data = {}  

    for url in DATABASE_URLS.values():
        #filtering from both databases
        query_url = f'{url}?orderBy="year"&equalTo={year}'
        response = requests.get(query_url)

        if response.status_code == 200:
            data = response.json()

            if data:
                combined_data.update(data)

        else:
            print(f"Error fetching data from {url}")

    return json.dumps(combined_data)



# Use the below main method to test your code
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python script.py [operation] [arguments]")
        
    operation = sys.argv[1].lower()
    if operation == "add_book":
        result = add_book(sys.argv[2], sys.argv[3])
        print(result)
    elif operation == "search_by_author":
        books = search_by_author(sys.argv[2])
        print(books)
    elif operation == "search_by_year":
        year = int(sys.argv[2])
        books = search_by_year(year)
        print(books)
