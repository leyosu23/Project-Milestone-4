import os

BASE_DIR = "BookKeeper_Project"
SRC_DIR = os.path.join(BASE_DIR, "src")

os.makedirs(SRC_DIR, exist_ok=True)

print(f"Creating project in: {os.path.abspath(BASE_DIR)}")

# ---------------------------------------------------------
# 1. requirements.txt
# ---------------------------------------------------------
requirements_content = "requests\n"

with open(os.path.join(BASE_DIR, "requirements.txt"), "w", encoding="utf-8") as f:
    f.write(requirements_content)

# ---------------------------------------------------------
# 2. src/__init__.py
# ---------------------------------------------------------
with open(os.path.join(SRC_DIR, "__init__.py"), "w", encoding="utf-8") as f:
    f.write("")

# ---------------------------------------------------------
# 3. src/models.py
# ---------------------------------------------------------
models_content = r'''from datetime import datetime, timedelta
from typing import Optional

class Book:
    """Book entity representing a book in the library collection."""
    def __init__(self, isbn: str, title: str, author: str,
                 pub_date: Optional[str] = None, genre: Optional[str] = None,
                 location: str = "Shelf A1", status: str = "available"):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.pub_date = pub_date
        self.genre = genre
        self.location = location
        self.status = status
        self.created_at = datetime.now().isoformat()

    def __repr__(self) -> str:
        return f"Book(isbn={self.isbn}, title='{self.title}', author='{self.author}')"

class Borrower:
    """Borrower entity representing a person who can checkout books."""
    def __init__(self, borrower_id: int, name: str, contact: str, email: Optional[str] = None):
        self.borrower_id = borrower_id
        self.name = name
        self.contact = contact
        self.email = email

    def __repr__(self) -> str:
        return f"Borrower(id={self.borrower_id}, name='{self.name}')"

class Loan:
    """Loan entity representing a book checkout/return transaction."""
    def __init__(self, loan_id: int, isbn: str, borrower_id: int,
                 checkout_date: Optional[str] = None, due_date: Optional[str] = None,
                 return_date: Optional[str] = None):
        self.loan_id = loan_id
        self.isbn = isbn
        self.borrower_id = borrower_id
        self.checkout_date = checkout_date or datetime.now().isoformat()
        self.due_date = due_date or (datetime.now() + timedelta(days=14)).isoformat()
        self.return_date = return_date

    def is_overdue(self) -> bool:
        if self.return_date:
            return False
        due = datetime.fromisoformat(self.due_date)
        return datetime.now() > due
'''

with open(os.path.join(SRC_DIR, "models.py"), "w", encoding="utf-8") as f:
    f.write(models_content)

# ---------------------------------------------------------
# 4. src/repositories.py
# ---------------------------------------------------------
repositories_content = r'''from typing import Dict, List, Optional
from .models import Book, Borrower, Loan

class BookRepository:
    """
    In-memory repository for Book entities.
    Implements Repository Pattern to abstract data access.
    """
    def __init__(self):
        self._books: Dict[str, Book] = {}

    def add(self, book: Book) -> None:
        self._books[book.isbn] = book

    def get(self, isbn: str) -> Optional[Book]:
        return self._books.get(isbn)

    def delete(self, isbn: str) -> bool:
        if isbn in self._books:
            del self._books[isbn]
            return True
        return False

    def get_all(self) -> List[Book]:
        return list(self._books.values())

class LoanRepository:
    """In-memory repository for Loan entities."""
    def __init__(self):
        self._loans: Dict[int, Loan] = {}
        self._next_id = 1

    def add(self, loan: Loan) -> int:
        if not loan.loan_id:
            loan.loan_id = self._next_id
            self._next_id += 1
        self._loans[loan.loan_id] = loan
        return loan.loan_id

    def get_active_loan_by_isbn(self, isbn: str) -> Optional[Loan]:
        for loan in self._loans.values():
            if loan.isbn == isbn and loan.return_date is None:
                return loan
        return None
    
    def get_all(self) -> List[Loan]:
        return list(self._loans.values())
'''

with open(os.path.join(SRC_DIR, "repositories.py"), "w", encoding="utf-8") as f:
    f.write(repositories_content)

# ---------------------------------------------------------
# 5. src/adapters.py
# ---------------------------------------------------------
adapters_content = r'''import requests
import os
from typing import Optional, Dict
from .models import Book

class GoogleBooksAdapter:
    """
    Adapter for Google Books API.
    Converts external API responses into internal Book objects.
    """
    BASE_URL = "https://www.googleapis.com/books/v1/volumes"
    API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY", "")

    @staticmethod
    def fetch_book_by_isbn(isbn: str) -> Optional[Dict]:
        try:
            params = {'q': f'isbn:{isbn}'}
            if GoogleBooksAdapter.API_KEY:
                params['key'] = GoogleBooksAdapter.API_KEY
            
            response = requests.get(GoogleBooksAdapter.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('totalItems', 0) > 0:
                return data['items'][0]['volumeInfo']
            return None
        except Exception as e:
            print(f"API Warning: Could not fetch data ({e})")
            return None

    @staticmethod
    def convert_to_book(api_response: Dict, isbn: str) -> Book:
        if not api_response:
            return Book(isbn=isbn, title="Unknown Title", author="Unknown Author")
            
        title = api_response.get('title', 'Unknown Title')
        authors = api_response.get('authors', ['Unknown Author'])
        
        if isinstance(authors, list):
            author = ', '.join(authors)
        else:
            author = str(authors)
            
        categories = api_response.get('categories', ['General'])
        if isinstance(categories, list):
            genre = ', '.join(categories)
        else:
            genre = str(categories)
        
        return Book(isbn=isbn, title=title, author=author, genre=genre)
'''

with open(os.path.join(SRC_DIR, "adapters.py"), "w", encoding="utf-8") as f:
    f.write(adapters_content)

# ---------------------------------------------------------
# 6. src/services.py
# ---------------------------------------------------------
services_content = r'''from typing import Optional, Dict
from datetime import datetime
from .models import Book, Borrower, Loan
from .repositories import BookRepository, LoanRepository
from .adapters import GoogleBooksAdapter

class LibraryService:
    """
    Service layer for library operations.
    Coordinates between UI, API integration, and repositories.
    """
    def __init__(self):
        self.book_repo = BookRepository()
        self.loan_repo = LoanRepository()
        self.borrowers: Dict[int, Borrower] = {}
        self.next_borrower_id = 1

    def add_book_from_isbn(self, isbn: str) -> Optional[Book]:
        if self.book_repo.get(isbn):
            print(f"Book {isbn} already exists.")
            return self.book_repo.get(isbn)

        api_data = GoogleBooksAdapter.fetch_book_by_isbn(isbn)
        book = GoogleBooksAdapter.convert_to_book(api_data, isbn)
        
        self.book_repo.add(book)
        print(f"✓ Book added: {book.title} by {book.author}")
        return book

    def create_borrower(self, name: str, contact: str, email: str = None) -> Borrower:
        borrower = Borrower(self.next_borrower_id, name, contact, email)
        self.borrowers[self.next_borrower_id] = borrower
        self.next_borrower_id += 1
        return borrower

    def checkout_book(self, isbn: str, borrower_id: int) -> Optional[Loan]:
        book = self.book_repo.get(isbn)
        if not book:
            print(f"Book {isbn} not found.")
            return None
        if book.status != 'available':
            print(f"Book {isbn} is not available.")
            return None

        loan = Loan(loan_id=0, isbn=isbn, borrower_id=borrower_id)
        self.loan_repo.add(loan)
        book.status = 'checked_out'
        print(f"✓ Book checked out. Due date: {loan.due_date}")
        return loan

    def checkin_book(self, isbn: str) -> Optional[Loan]:
        loan = self.loan_repo.get_active_loan_by_isbn(isbn)
        if not loan:
            print(f"No active loan found for ISBN {isbn}")
            return None
        
        loan.return_date = datetime.now().isoformat()
        book = self.book_repo.get(isbn)
        if book:
            book.status = 'available'
        print(f"✓ Book returned successfully.")
        return loan

    def generate_report(self) -> Dict:
        books = self.book_repo.get_all()
        total = len(books)
        available = sum(1 for b in books if b.status == 'available')
        return {
            'total_books': total,
            'available': available,
            'checked_out': total - available
        }
'''

with open(os.path.join(SRC_DIR, "services.py"), "w", encoding="utf-8") as f:
    f.write(services_content)

# ---------------------------------------------------------
# 7. main.py
# ---------------------------------------------------------
main_content = r'''from src.services import LibraryService
import sys

def demo():
    print("=" * 60)
    print("BookKeeper - Library Management System")
    print("Architecture: 4+1 View Model Implementation")
    print("=" * 60)

    service = LibraryService()

    print("\n[1] Adding book via Google Books API (Adapter Pattern)...")
    isbn = "9780134685991" # Clean Code
    book = service.add_book_from_isbn(isbn)

    print("\n[2] Creating borrower...")
    borrower = service.create_borrower("Alice Kim", "010-1234-5678")
    print(f"Created: {borrower}")

    if book:
        print("\n[3] Checking out book...")
        service.checkout_book(isbn, borrower.borrower_id)

    print("\n[4] Generating Availability Report...")
    report = service.generate_report()
    print(f"Total Books: {report['total_books']}")
    print(f"Available: {report['available']}")
    print(f"Checked Out: {report['checked_out']}")

    print("\n[5] Checking in book...")
    service.checkin_book(isbn)
    
    print("\n" + "="*60)
    print("Demo Completed Successfully.")

if __name__ == "__main__":
    demo()
'''

with open(os.path.join(BASE_DIR, "main.py"), "w", encoding="utf-8") as f:
    f.write(main_content)

print("Success! All files created.")
