# NarrativeNet API Documentation

## Authentication Endpoints

### 1. Obtain JWT Token
- *Endpoint:* /api/token/
- *Method:* POST
- *Description:* Obtain a JSON Web Token (JWT) by providing valid credentials.
- *Request:*
  - Body:
    json
    {
        "username": "your_username",
        "password": "your_password"
    }
    
- *Response:*
  - Successful response:
    json
    {
        "access": "your_access_token",
        "refresh": "your_refresh_token"
    }
    
  - Error response (e.g., invalid credentials):
    json
    {
        "detail": "Invalid credentials"
    }
    

### 2. Refresh JWT Token
- *Endpoint:* /api/token/refresh/
- *Method:* POST
- *Description:* Refresh an expired JWT by providing a valid refresh token.
- *Request:*
  - Body:
    json
    {
        "refresh": "your_refresh_token"
    }
    
- *Response:*
  - Successful response:
    json
    {
        "access": "your_new_access_token"
    }
    
  - Error response (e.g., invalid refresh token):
    json
    {
        "detail": "Invalid refresh token"
    }
    

## Books Endpoints

### 1. Get All Books
- *Endpoint:* /api/books/
- *Method:* GET
- *Description:* Retrieve a list of all books.
- *Response:*
  - Successful response:
    json
    [
        {
            "book_id": 1,
            "title": "Romance and Dummy Book 3",
            "synopsis": "Experience a tale of love and passion...",
            "views": 2000,
            "rating": "4.2",
            "genres": ["Romance", "Drama"]
        },
        // ... Other books
    ]
    
  - Error response (e.g., books not found):
    json
    {
        "detail": "No books available."
    }
    

### 2. Get Books by Genre
- *Endpoint:* /api/books/<str:genre_name>/
- *Method:* GET
- *Description:* Retrieve a list of books filtered by genre(s).
- *Parameters:*
  - genre_name (string): Comma-separated list of genres.
- *Response:*
  - Successful response:
    json
    [
        {
            "book_id": 1,
            "title": "Romance and Dummy Book 3",
            "synopsis": "Experience a tale of love and passion...",
            "views": 2000,
            "rating": "4.2",
            "genres": ["Romance", "Drama"]
        },
        // ... Other books matching the specified genre(s)
    ]
    
  - Error response (e.g., books not found for the specified genre):
    json
    {
        "detail": "No books available for the specified genre(s)."
    }
    