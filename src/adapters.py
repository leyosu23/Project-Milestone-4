import requests
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
