import requests
from bs4 import BeautifulSoup
from datetime import datetime, time
from flask import Flask, jsonify, request, make_response
from flask_restful import Resource, Api

app = Flask(__name__) # Instance of flask
api = Api(app)

worcester_url = 'https://umassdining.com/locations-menus/worcester/menu'
blue_wall_url = 'https://umassdining.com/menu/harvest-blue-wall-menu'

def get_menu_contents(menu_url):
    response = requests.get(menu_url)
    return response.text


def parse_menu_contents(menu_contents, specific_menu):
    wbdoc = BeautifulSoup(menu_contents, 'html.parser')
    div = wbdoc.find('div', {'id': specific_menu})
    food_tags = div.find_all('li', {'class': 'lightbox-nutrition'})
    food_items_set = set()
    for food in food_tags:
        food_name_tag = food.select_one('a')
        if food_name_tag:
            food_name = food_name_tag.text.strip()
            protein_content = food_name_tag.get('data-protein', 'N/A')
            carbs_content = food_name_tag.get('data-total-carb', 'N/A')
            fat_content = food_name_tag.get('data-total-fat', 'N/A')
            calories = food_name_tag.get('data-calories', 'N/A')
            food_items_set.add((food_name, calories, protein_content, carbs_content, fat_content))
        else:
            print("Skipping a food item due to missing 'a' tag.")
    return food_items_set



def sort_menu(food_items_set):
    return sorted(food_items_set, key=lambda x: (float(x[2].rstrip('g')) / max(float(x[1]), 1), -float(x[1])), reverse=True)

def is_lunch_time():
    current_time = datetime.now().time()
    lunch_start_time = time(11, 0)  # Adjust this to your desired lunch start time
    lunch_end_time = time(16, 30)  # Adjust this to your desired lunch end time
    return lunch_start_time <= current_time <= lunch_end_time

def is_breakfast_time():
    current_time = datetime.now().time()
    b_start_time = time(7, 0)
    b_end_time = time(10,59)
    return b_start_time <= current_time <= b_end_time

def is_dinner_time():
    current_time = datetime.now().time()
    d_start_time = time(16, 31)
    d_end_time = time(21,0)
    return d_start_time <= current_time <= d_end_time
    


@app.route('/menu', methods=['GET'])
def get_menu():
    if is_lunch_time():
        lunch_menu_contents = get_menu_contents(blue_wall_url)
        lunch_menu_items = parse_menu_contents(lunch_menu_contents, 'lunch_menu')
        if lunch_menu_items:
            sorted_lunch_menu = sort_menu(lunch_menu_items)
            return jsonify(sorted_lunch_menu)
    if is_breakfast_time:
        breakfast_menu_contents = get_menu_contents(blue_wall_url)
        breakfast_menu_items = parse_menu_contents(breakfast_menu_contents, 'breakfast_menu')
        if breakfast_menu_items:
            sorted_breakfast_menu = sort_menu(breakfast_menu_items)
            return jsonify(sorted_breakfast_menu)
        
    if is_dinner_time:
        dinner_menu_contents = get_menu_contents(blue_wall_url)
        dinner_menu_items = parse_menu_contents(dinner_menu_contents, 'dinner_menu')
        if dinner_menu_items:
            sorted_dinner_menu = sort_menu(dinner_menu_items)
            return jsonify(sorted_dinner_menu)
        
    else:
     return jsonify({"message": "Menu not available at the moment."})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)

    
