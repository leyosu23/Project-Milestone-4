from typing import Optional, Dict
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
