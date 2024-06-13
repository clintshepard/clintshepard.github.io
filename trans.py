import json

# Чтение исходного файла recipes.json
with open('recipes.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Преобразование структуры
base_ingredients = data.get('base_ingredients', [])
recipes_dict = data.get('recipes', {})

# Преобразование рецептов в список
recipes = []
for name, details in recipes_dict.items():
    recipe = {
        "name": name,
        "ingredients": details["ingredients"],
        "output": details["output"],
        "heat": details["heat"],
        "type": details["type"]
    }
    recipes.append(recipe)

# Новая структура данных
new_data = {
    "base_ingredients": base_ingredients,
    "recipes": recipes
}

# Запись преобразованных данных в новый файл
with open('new_recipes.json', 'w', encoding='utf-8') as file:
    json.dump(new_data, file, ensure_ascii=False, indent=4)

print("Преобразование завершено. Новый файл сохранен как new_recipes.json")
