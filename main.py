from src.services import LibraryService
import sys

def demo():
    print("=" * 2)
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
