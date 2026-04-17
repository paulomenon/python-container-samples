from flask import Flask, jsonify, request

app = Flask(__name__)

books = [
    {"id": 1, "title": "The Pragmatic Programmer", "author": "David Thomas", "year": 1999},
    {"id": 2, "title": "Clean Code", "author": "Robert C. Martin", "year": 2008},
    {"id": 3, "title": "Design Patterns", "author": "Gang of Four", "year": 1994},
]
next_id = 4


@app.route("/")
def index():
    return jsonify({"service": "Book REST API", "version": "1.0"})


@app.route("/api/books", methods=["GET"])
def list_books():
    return jsonify({"count": len(books), "books": books})


@app.route("/api/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book)


@app.route("/api/books", methods=["POST"])
def create_book():
    global next_id
    data = request.get_json()
    book = {"id": next_id, "title": data["title"], "author": data["author"], "year": data.get("year", 0)}
    next_id += 1
    books.append(book)
    return jsonify(book), 201


@app.route("/api/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    data = request.get_json()
    book.update({k: data[k] for k in ("title", "author", "year") if k in data})
    return jsonify(book)


@app.route("/api/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    global books
    before = len(books)
    books = [b for b in books if b["id"] != book_id]
    if len(books) == before:
        return jsonify({"error": "Book not found"}), 404
    return jsonify({"message": "Deleted"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
