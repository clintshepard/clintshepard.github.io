from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

# Загрузка данных из JSON файла
with open('./recipes.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

base_ingredients = data["base_ingredients"]
recipes = data["recipes"]
comments = data["comments"]

# Порядок сортировки категорий
category_order = [
    "Component", "Basic", "Superior Medicine", "Other Medicine",
    "Drugs", "Toxins", "Boom", "Food", "Miscellaneous"
]

# Сортировка рецептов по типам
recipes_by_type = {}
for recipe_name, recipe_info in recipes.items():
    recipe_type = recipe_info.get('type')
    if recipe_type not in recipes_by_type:
        recipes_by_type[recipe_type] = []
    recipes_by_type[recipe_type].append(recipe_name)

# Сортировка словаря по заданному порядку категорий
sorted_recipes_by_type = {category: recipes_by_type[category] for category in category_order if category in recipes_by_type}


def calculate_ingredients(substance, quantity):
    if substance in base_ingredients:
        return {substance: {"quantity": quantity, "components": {}}}

    if substance not in recipes:
        return {}

    result = {}
    ingredients = recipes[substance]["ingredients"]
    output_qty = recipes[substance]["output"]
    multiplier = quantity / output_qty

    for ingredient, amount in ingredients.items():
        sub_result = calculate_ingredients(ingredient, amount * multiplier)
        if ingredient in result:
            for sub_ingredient, sub_info in sub_result.items():
                if sub_ingredient in result[ingredient]["components"]:
                    result[ingredient]["components"][sub_ingredient]["quantity"] += sub_info["quantity"]
                else:
                    result[ingredient]["components"][sub_ingredient] = sub_info
        else:
            result[ingredient] = {
                "quantity": amount * multiplier,
                "components": sub_result
            }

    return result


def format_ingredients(ingredients, level=0, include_sublevels=True):
    result_str = ""
    indent = "----" * level
    for ingredient, info in ingredients.items():
        result_str += f"{indent}{ingredient}: {info['quantity']:.2f}\n"
        if include_sublevels and info["components"]:
            if ingredient not in base_ingredients:
                result_str += format_ingredients(info["components"], level + 1, include_sublevels)
    return result_str


@app.route('/')
def index():
    return render_template('index.html'), recipes_by_type=sorted_recipes_by_type, base_ingredients=base_ingredients)


@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    substance = data['substance']
    quantity = data['quantity']
    include_sublevels = data.get('includeSublevels', True)

    try:
        quantity = float(quantity)  # Преобразование строки в число с плавающей точкой
    except ValueError:
        return jsonify(result="Некорректное количество. Введите числовое значение.")

    if not substance:
        return jsonify(result="Выберите вещество.")

    ingredients = calculate_ingredients(substance, quantity)
    result_str = format_ingredients(ingredients, include_sublevels=include_sublevels)

    if substance in recipes:
        heat_info = recipes[substance].get("heat", {})
        if heat_info.get("required", False):
            result_str += f"\nНагреть до {heat_info['temperature']}°K."

    if substance in comments:
        result_str += f"\nКомментарий: {comments[substance]}"

    return jsonify(result=result_str)


if __name__ == '__main__':
    app.run(debug=True)
