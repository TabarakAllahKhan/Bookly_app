from src.books.schemas import BookCreateModel
books_prefix=f"/api/v1/books"

book_create_data={
    "title":"get started with golang",
    "author":"Tabarak",
    "year":2018,
    "isbn":"9990001",
    "pages":200,
    "price":20.99,
    "available":True,
    "summary":"a nice book"
}

def get_all_books(test_client,test_book_service,test_session):
    res=test_client.post(
        url=f"{books_prefix}",
        json=book_create_data
        
    )
    book_data=BookCreateModel(**book_create_data)
    assert test_book_service.get_all_books_once()
    assert test_book_service.get_all_books_once_with(test_session)
    assert test_book_service.create_book_once_with(test_session,book_data)