from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

connection_string = "mongodb+srv://userReadOnly:7ZT817O8ejDfhnBM@minichallenge.q4nve1r.mongodb.net/"
client = MongoClient(connection_string)
db = client['minichallenge']
collection_flight = db['flights'] 
collection_hotel = db['hotels'] 

@app.route('/flight', methods=['GET'])
def get_flight_info():
    departure_date = request.args.get('departureDate')
    return_date = request.args.get('returnDate')
    destination = request.args.get('destination')

    if not departure_date or not return_date or not destination:
        return jsonify({"error": "Missing query parameters"}), 400

    try:
        departure_date = datetime.strptime(departure_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
        return_date = datetime.strptime(return_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)

    except ValueError:
        return jsonify({"error": "Incorrect date format. Please use YYYY-MM-DD"}), 400

    query_dept = {
        'date': departure_date,
        'srccity': 'Singapore',
        'destcity': {'$regex': f'^{destination}$', '$options': 'i'}
    }
    results_dept = collection_flight.find(query_dept)

    query_ret = {
        'date': return_date,
        'srccity': {'$regex': f'^{destination}$', '$options': 'i'},
        'destcity': 'Singapore'
    }
    results_ret = collection_flight.find(query_ret)

    cheapest_flights = []
    lowest_price = float('inf')

    for result_dept in results_dept:
        for result_ret in results_ret:
            total_price = result_dept['price'] + result_ret['price']
            if total_price <= lowest_price:
                lowest_price = total_price
                flight_data = {
                    "City": result_dept['destcity'],
                    "Departure Date": result_dept['date'],
                    "Departure Airline": result_dept['airlinename'],
                    "Departure Price": result_dept['price'],
                    "Return Date": result_ret['date'],
                    "Return Airline": result_ret['airlinename'],
                    "Return Price": result_ret['price']
                }
                cheapest_flights.append(flight_data)

    return jsonify(flight_data), 200

@app.route('/hotel', methods=['GET'])
def get_hotel_info():
    checkIn_date = request.args.get('checkInDate')
    checkOut_date = request.args.get('checkOutDate')
    destination = request.args.get('destination')

    if not checkIn_date or not checkOut_date or not destination:
        return jsonify({"error": "Missing query parameters"}), 400

    try:
        checkIn_date = datetime.strptime(checkIn_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
        checkOut_date = datetime.strptime(checkOut_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)

    except ValueError:
        return jsonify({"error": "Incorrect date format. Please use YYYY-MM-DD"}), 400

    query = {
        'city': destination,
        'date': {'$gte': checkIn_date, '$lte': checkOut_date}
    }

    results = collection_hotel.aggregate([
        {'$match': query},
        {'$group': {'_id': {'hotelName': '$hotelName', 'city': '$city'}, 'totalPrice': {'$sum': '$price'}}},
        {'$sort': {'totalPrice': 1}}
    ])

    cheapest_hotel = []
    lowest_price = float('inf')

    for result in results:
        if result['totalPrice'] <= lowest_price:
            lowest_price = result['totalPrice']
            hotel_data = {
                "City": result['_id']['city'],
                "Check In Date": checkIn_date.strftime('%Y-%m-%d'),
                "Check Out Date": checkOut_date.strftime('%Y-%m-%d'),
                "Hotel": result['_id']['hotelName'],
                "Price": result['totalPrice']
            }
            cheapest_hotel.append(hotel_data)

    return jsonify(cheapest_hotel), 200

if __name__ == '__main__':
    app.run('0.0.0.0', port=8080)
