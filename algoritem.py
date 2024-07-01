import pandas as pd

# קריאת קובץ האקסל עם הנתיב המעודכן
file_path = 'C:/Users/נעה/Desktop/תעשייה וניהול/שנה ב/סמסטר ב/חקבצ 2/פרויקט/data project.xlsx'
ingredients_data = pd.read_excel(file_path, sheet_name='Ingredients')
dishes_data = pd.read_excel(file_path, sheet_name='Dishs')

# דוגמה לשימוש בקלטים מהמשתמש
budget = float(input("הכנס את התקציב המקסימלי: "))
required_dish = input("הכנס מנה שחייבת להיות בתכנון: ").strip().lower()  # הסרת רווחים מיותרים והמרה לאותיות קטנות
allergies = input("הכנס אלרגיות (מופרדות בפסיקים): ").split(',')

# ניקוי אלרגיות מיותרים והמרה לאותיות קטנות
allergies = [allergy.strip().lower() for allergy in allergies if allergy.strip()]

print("\nRequired Dish:", required_dish)
print("Allergies:", allergies)

# המרת שמות המנות והמרכיבים לאותיות קטנות לצורך השוואה
dishes_data['Dish'] = dishes_data['Dish'].str.lower()
for i in range(1, 6):
    dishes_data[f'Ingredients {i}'] = dishes_data[f'Ingredients {i}'].str.lower()

ingredients_data['Ingredient'] = ingredients_data['Ingredient'].str.lower()

# אלגוריתם לבחירת מנות אופטימליות
def optimized_selection(budget, required_dish, allergies, ingredients_data, dishes_data):
    # סינון המנות על פי אלרגיות
    def filter_dishes(dishes, allergies):
        if not allergies:
            return dishes
        filtered_dishes = []
        for index, row in dishes.iterrows():
            if not any(allergy in row[f'Ingredients {i}'] for allergy in allergies for i in range(1, 6) if pd.notna(row[f'Ingredients {i}'])):
                filtered_dishes.append(row)
        return pd.DataFrame(filtered_dishes)

    # חישוב עלות כוללת של מרכיבים בכל מנה
    def calculate_dish_cost(dish, ingredients_data):
        total_cost = 0
        for i in range(1, 6):
            ingredient = dish[f'Ingredients {i}']
            if pd.notna(ingredient):
                ingredient_price_row = ingredients_data[ingredients_data['Ingredient'] == ingredient]
                if not ingredient_price_row.empty:
                    ingredient_price = ingredient_price_row['price'].values[0]
                    total_cost += ingredient_price
                else:
                    print(f"Warning: Ingredient '{ingredient}' not found in ingredients data.")
        return total_cost

    # בדיקת המנה הנדרשת לפני סינון המנות
    if required_dish:
        required_dish_row = dishes_data[dishes_data['Dish'] == required_dish]
        if required_dish_row.empty:
            return f"המנה '{required_dish}' אינה קיימת במאגר.", None, None, None, None, None
        for i in range(1, 6):
            ingredient = required_dish_row.iloc[0][f'Ingredients {i}']
            if pd.notna(ingredient) and any(allergy == ingredient for allergy in allergies):
                return f"המנה המבוקשת '{required_dish}' מכילה את האלרגיה שלך '{ingredient}' ולכן לא ניתן לבחור בה.", None, None, None, None, None

    # סינון המנות על פי אלרגיות
    dishes_data = filter_dishes(dishes_data, allergies)

    # אם אין מנה חובה, לבחור מנות באופן חופשי
    selected_dishes = []
    if required_dish:
        required_dish_row = dishes_data[dishes_data['Dish'] == required_dish].iloc[0]
        required_dish_cost = calculate_dish_cost(required_dish_row, ingredients_data)
        if required_dish_cost > budget:
            return "עלות המנה הנדרשת גבוהה מהתקציב", None, None, None, None, None
        selected_dishes.append(required_dish_row)
        budget -= required_dish_cost

    # מיון המנות לפי הערך התזונתי בסדר יורד
    dishes_data = dishes_data.sort_values(by='Nutritional Value', ascending=False)

    # בחירת מנות נוספות לפי הערך התזונתי הגבוה ביותר במסגרת התקציב
    for index, row in dishes_data.iterrows():
        if row['Dish'] != required_dish:
            dish_cost = calculate_dish_cost(row, ingredients_data)
            if dish_cost <= budget:
                selected_dishes.append(row)
                budget -= dish_cost

    # חישוב רשימת המצרכים, העלות הכוללת, והערך התזונתי של הסל
    ingredients = {}
    total_cost = 0
    for dish in selected_dishes:
        for i in range(1, 6):
            ingredient = dish[f'Ingredients {i}']
            if pd.notna(ingredient):
                # חישוב עלות המצרכים
                ingredient_price_row = ingredients_data[ingredients_data['Ingredient'] == ingredient]
                if not ingredient_price_row.empty:
                    ingredient_price = ingredient_price_row['price'].values[0]
                    total_cost += ingredient_price
                    if ingredient in ingredients:
                        ingredients[ingredient] += 1
                    else:
                        ingredients[ingredient] = 1
                else:
                    print(f"Warning: Ingredient '{ingredient}' not found in ingredients data.")

    # הכנת רשימת המצרכים עם הכפולות המתאימות
    ingredients_list = [f"{ingredient}*{count}" if count > 1 else ingredient for ingredient, count in ingredients.items()]

    remaining_budget = budget
    selected_dish_names = [dish['Dish'] for dish in selected_dishes]
    total_nutritional_value = sum(dish['Nutritional Value'] for dish in selected_dishes)

    return selected_dish_names, ingredients_list, total_cost, total_nutritional_value, remaining_budget

# הפעלת הפונקציה והצגת הפלט
result = optimized_selection(budget, required_dish, allergies, ingredients_data, dishes_data)

if result[1] is None:
    print(result[0])
else:
    selected_dish_names, ingredients_list, total_cost, total_nutritional_value, remaining_budget = result
    print(f"נבחרו המנות הבאות: {selected_dish_names}")
    print(f"רשימת המצרכים: {ingredients_list}")
    print(f"עלות כוללת: {total_cost:.3f}")
    print(f"ערך תזונאי של הסל: {total_nutritional_value:.3f}")
    print(f"עודף: {remaining_budget:.3f}")
