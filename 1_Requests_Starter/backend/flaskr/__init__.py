import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy  # , or_
from flask_cors import CORS
import random

from models import setup_db, Book

BOOKS_PER_SHELF = 8

# @TODO: General Instructions
#   - As you're creating endpoints, define them and then search for 'TODO' within the frontend to update the endpoints there.
#     If you do not update the endpoints, the lab will not work - of no fault of your API code!
#   - Make sure for each route that you're thinking through when to abort and with which kind of error
#   - If you change any of the response body keys, make sure you update the frontend to correspond.


def paginate_books(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * BOOKS_PER_SHELF
    end = start + BOOKS_PER_SHELF
    books = [book.format() for book in selection]
    books_on_page = books[start:end]
    return books_on_page

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)


    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    # @DONE Write a route that retrivies all books, paginated.
    #         You can use the constant above to paginate by eight books.
    #         If you decide to change the number of books per page,
    #         update the frontend to handle additional books in the styling and pagination
    #         Response body keys: 'success', 'books' and 'total_books'
    @app.route('/books/', methods=['GET'])
    def get_books():
        selection = Book.query.all()
        books = paginate_books(request, selection)
        #if the page contains some books
        if len(books):
            return jsonify({
                "success": True,
                "books" : books,
                "total_books" : len(selection)
            })
        else:
            abort(404)
    # TEST: When completed, the webpage will display books including title, author, and rating shown as stars

    # @DONE Write a route that will update a single book's rating.
    #         It should only be able to update the rating, not the entire representation
    #         and should follow API design principles regarding method and route.
    #         Response body keys: 'success'
    @app.route('/books/<int:book_id>', methods=['PATCH'])
    def changeRating(book_id):

        body = request.get_json()

        try:
            book = Book.query.filter(Book.id == book_id).one_or_none()

            if book is None:
                abort(404)

            if 'rating' in body:
                book.rating = int(body['rating'])

            book.update()

            return jsonify({
                "success" : True,
                'id' : book.id
            })

        except:
            abort(400)
    # TEST: When completed, you will be able to click on stars to update a book's rating and it will persist after refresh

    # @DONE: Write a route that will delete a single book.
    #        Response body keys: 'success', 'deleted'(id of deleted book), 'books' and 'total_books'
    #        Response body keys: 'success', 'books' and 'total_books'
    @app.route('/books/<int:book_id>', methods=['DELETE'])
    def delete_book(book_id):
        
        try:
            book = Book.query.filter(Book.id==book_id).one_or_none()
            if book is None:
                abort(404)

            book.delete()
            total_books = Book.query.order_by(Book.id).all()
            books = paginate_books(request, total_books)
            return jsonify({
                "success": True,
                "deleted" : book_id,
                "books" : books,
                "total_books" : len(total_books)
            })
        except:
            abort(422)


    # TEST: When completed, you will be able to delete a single book by clicking on the trashcan.

    # @DONE: Write a route that create a new book.
    #        Response body keys: 'success', 'created'(id of created book), 'books' and 'total_books'
    @app.route('/books/', methods=['POST'])
    def submit_book():
        body = request.get_json()

        title = body.get('title', None)
        author = body.get('author', None)
        rating = body.get('rating', None)

        try:
            book = Book(title=title, author=author, rating=rating)
            book.insert()
            total_books = Book.query.order_by(Book.id).all()
            books = paginate_books(request, total_books)
            return jsonify({
                "success" : True,
                "created" : book.id,
                "books" : books,
                "total_books" : len(total_books)
            })

        except:
            abort(422)
    # TEST: When completed, you will be able to a new book using the form. Try doing so from the last page of books.
    #       Your new book should show up immediately after you submit it at the end of the page.
    

    #
    @app.errorhandler(404)
    def notFound(error):
        return jsonify({
            "success" : "false",
            "error" : 404,
            "message" : "Resource not found",
        }), 404

    @app.errorhandler(400)
    def badRequest(error):
        return jsonify({
            "success" : "false",
            "error" : 400,
            "message" : "You entered a bad request",
        }), 400

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success" : "false",
            "error" : 422,
            "message" : "Unprocessable Entity",
        }), 422
    
    @app.errorhandler(405)
    def methodNotAllowed(error):
        return jsonify({
            "success" : "false",
            "error" : 405,
            "message" : "Method Not Allowed",
        }), 405


    return app
