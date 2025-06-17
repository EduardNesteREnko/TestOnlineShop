from flask import Flask,render_template,request,redirect, request, jsonify
from  flask_sqlalchemy import  SQLAlchemy
import stripe
import os
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    isActive = db.Column(db.Boolean, default=True)
    #text = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return self.title

@app.route('/')
def index():
    items = Item.query.order_by(Item.price).all()
    return  render_template('index.html', data=items)

@app.route('/about')
def about():
    return  render_template('about.html')

@app.route('/create', methods=['POST',"GET"])
def create():
    if request.method =='POST':
        title = request.form['title']
        price = request.form['price']

        item = Item(title=title,  price=price)

        try:
            db.session.add(item)
            db.session.commit()
            return redirect('/')
        except:
            return "Something went wrong"

    else:
        return  render_template('create.html')

@app.route('/buy/<int:id>', methods=['POST'])
def buy(id):
    item = Item.query.get(id)
    if item is None:
        return "Товар не найден", 404

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': item.title,
                },
                'unit_amount': item.price * 100,  # в центах!
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.host_url + 'success',
        cancel_url=request.host_url + 'cancel',
    )
    return redirect(session.url, code=303)

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/cancel')
def cancel():
    return render_template('cancel.html')


if __name__== '__main__':
    app.run(debug=True)