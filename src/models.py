from datetime import datetime, timedelta
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
