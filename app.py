from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flashcards.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(256), nullable=False)
    answer = db.Column(db.String(256), nullable=False)
    interval = db.Column(db.Integer, default=1)
    next_review = db.Column(db.Date, default=datetime.date.today)

# Initialize database
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/browse')
def browse():
    cards = Card.query.all()
    return render_template('browse.html', cards=cards)

@app.route('/add_card', methods=['POST'])
def add_card():
    data = request.json
    question = data.get('question')
    answer = data.get('answer')

    if not question or not answer:
        return jsonify({"error": "Question and answer are required"}), 400

    new_card = Card(question=question, answer=answer)
    db.session.add(new_card)
    db.session.commit()

    return jsonify({"message": "Card added successfully"}), 201

@app.route('/delete_card/<int:card_id>', methods=['DELETE'])
def delete_card(card_id):
    card = Card.query.get(card_id)
    if not card:
        return jsonify({"error": "Card not found"}), 404

    db.session.delete(card)
    db.session.commit()

    return jsonify({"message": "Card deleted successfully"})

@app.route('/edit_card/<int:card_id>', methods=['POST'])
def edit_card(card_id):
    card = Card.query.get(card_id)
    if not card:
        return jsonify({"error": "Card not found"}), 404

    data = request.json
    question = data.get('question')
    answer = data.get('answer')

    if not question or not answer:
        return jsonify({"error": "Question and answer are required"}), 400

    card.question = question
    card.answer = answer
    db.session.commit()

    return jsonify({"message": "Card updated successfully"})

@app.route('/review', methods=['GET'])
def review():
    today = datetime.date.today()
    card = Card.query.filter(Card.next_review <= today).first()
    if card:
        return render_template('review.html', question=card.question, answer=card.answer, card_id=card.id)
    else:
        return "No cards due for review."

@app.route('/update_review/<int:card_id>', methods=['POST'])
def update_review(card_id):
    card = Card.query.get(card_id)
    if not card:
        return jsonify({"error": "Card not found"}), 404

    data = request.json
    success = data.get('success')

    if success:
        card.interval = card.interval * 2
    else:
        card.interval = 1

    card.next_review = datetime.date.today() + datetime.timedelta(days=card.interval)
    db.session.commit()

    return jsonify({"message": "Review updated successfully"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5675)
