#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, jsonify, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db,render_as_batch=True)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"
@app.route('/restaurants', methods=['GET'])
def restaurant():
        restaurants = []
        for restaurant in Restaurant.query.all():
            restaurant_dict={
                'id':restaurant.id,
                'name':restaurant.name,
                'address':restaurant.address
            }
            restaurants.append(restaurant_dict)
            response= make_response(
                jsonify(restaurants),
                200
                 )
        return response
    
@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurants(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
       restaurants_dict = {
            'id': restaurant.id,
            'name': restaurant.name,
            'address': restaurant.address,
            'restaurant_pizzas': [
                {
                    'id': pizza.id,
                    'restaurant_id': pizza.restaurant_id,
                    'pizza_id': pizza.pizza_id,
                    'price': pizza.price,
                    'pizza': {
                        'id': pizza.pizza.id,
                        'name': pizza.pizza.name,
                        'ingredients': pizza.pizza.ingredients
                    }
                }
                for pizza in restaurant.restaurant_menu
            ]
        }
       response= make_response(
        jsonify(restaurants_dict),
        200
        )
       return response
    
    else:
        response= make_response(
            jsonify({'error': 'Restaurant not found'}),
            404
        )
    return response
@app.route('/restaurant_pizzas',methods=['POST'])
def add_post():
    if request.method == 'POST':
       try:
            restaurant_pizzas= RestaurantPizza(
                 price = request.get_json()["price"],
                 restaurant_id= request.get_json()["restaurant_id"],
                 pizza_id= request.get_json()["pizza_id"]
            )
            db.session.add(restaurant_pizzas)
            db.session.commit()
            response= make_response(restaurant_pizzas.to_dict(),201,{"content-type":"application/json"})
            return response
       except ValueError as e:
            message={"errors":["validation errors"]}
            response= make_response(message,400)
            return response
            

            
@app.route('/restaurants/<int:id>',methods=['DELETE'])
def delete_restaurants(id):
    restaurant = Restaurant.query.filter_by(id=id).first()
    if restaurant:
       RestaurantPizza.query.filter_by(restaurant_id=id).delete()
       db.session.delete(restaurant)
       db.session.commit()
       response= make_response(
             jsonify({'message': 'The Named Restaurant is deleted successfully'}),
             204
            )
       return response
    else:
        response= make_response(
             jsonify({  "error": "Restaurant not found"}),
             404
            )
        return response
@app.route('/pizzas', methods=['GET'])
def get_pizzas():
        pizza_display=[]
        for pizza in Pizza.query.all():
            pizza_dict={
                'id':pizza.id,
                'ingredients': pizza.ingredients,
                'name': pizza.name,
            }
            pizza_display.append(pizza_dict)
            response= make_response(
                jsonify(pizza_display),
                200
            )
        return response
 


if __name__ == "__main__":
    app.run(port=5555, debug=True)
