from typing import Dict, List, Optional
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
