import sys

from database import Database

# sqlite queries to create tables
sql_create_tables_queries = [
    '''CREATE TABLE IF NOT EXISTS meals (meal_id INTEGER PRIMARY KEY, meal_name TEXT UNIQUE NOT NULL);''',
    '''CREATE TABLE IF NOT EXISTS ingredients (ingredient_id INTEGER PRIMARY KEY,
                                                ingredient_name TEXT UNIQUE NOT NULL);''',
    '''CREATE TABLE IF NOT EXISTS measures (measure_id INTEGER PRIMARY KEY,
                                            measure_name TEXT UNIQUE);''',
    '''CREATE TABLE IF NOT EXISTS recipes (recipe_id INTEGER PRIMARY KEY, recipe_name TEXT NOT NULL,
                                            recipe_description TEXT);''',
    '''CREATE TABLE IF NOT EXISTS serve (serve_id INTEGER PRIMARY KEY, meal_id INTEGER NOT NULL,
                            recipe_id INTEGER NOT NULL, FOREIGN KEY(meal_id) REFERENCES meals(meal_id),
                                            FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id));''',
    '''CREATE TABLE IF NOT EXISTS quantity (quantity_id INTEGER PRIMARY KEY, quantity INTEGER NOT NULL,
            recipe_id INTEGER NOT NULL, measure_id INTEGER NOT NULL, ingredient_id INTEGER NOT NULL,
                                            FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id),
                                            FOREIGN KEY(measure_id) REFERENCES measures(measure_id),
                                            FOREIGN KEY(ingredient_id) REFERENCES ingredients(ingredient_id))'''
]


def main():
    database = sys.argv[1]
    data = {"meals": ("breakfast", "brunch", "lunch", "supper"),
            "ingredients": ("milk", "cacao", "strawberry", "blueberry", "blackberry", "sugar"),
            "measures": ("ml", "g", "l", "cup", "tbsp", "tsp", "dsp", "")}
    recipes = []
    quantities = []

    # create a database connection
    with Database(database) as blog_database:
        if blog_database.conn is not None:
            # create meals, ingredients, measures, recipes tables
            blog_database.create_tables(sql_create_tables_queries)

            # insert data into tables meals, ingredients, measures
            blog_database.insert_data(data["meals"], "meals")
            blog_database.insert_data(data["ingredients"], "ingredients")
            blog_database.insert_data(data["measures"], "measures")

            # ask user for recipes
            print("Pass the empty recipe name to exit.")
            while recipe_name := input("Recipe name: "):
                recipe_description = input("Recipe description: ")
                for meal in blog_database.conn.execute("SELECT * FROM meals"):
                    print(f"{meal[0]}) {meal[1]}", end=" ")
                meals_to_serve = list(map(int, input("\nEnter proposed meals separated by a space: ").split(" ")))
                recipes.append((recipe_name, recipe_description, meals_to_serve))
                while ingred_quant_measure := input("Input quantity of ingredient <press enter to stop>: ").split():
                    measure_ingredient = {
                        "measure": "" if len(ingred_quant_measure) == 2 else ingred_quant_measure[1],
                        "ingredient": ingred_quant_measure[1] if len(ingred_quant_measure) == 2 else
                        ingred_quant_measure[2]}
                    measure_ingredient_ids = []
                    for table in list(measure_ingredient.keys()):
                        blog_database.cursor.execute(f"SELECT {table}_id FROM {table}s WHERE {table}_name "
                                                     f"LIKE '%{measure_ingredient[table]}%'" if measure_ingredient[
                                                                                                    table] != "" else
                                                     f"SELECT {table}_id FROM {table}s WHERE {table}_name LIKE ''")
                        sql_check = blog_database.cursor.fetchall()
                        if 1 < len(sql_check):
                            print(f"The {table} is not conclusive!")
                            continue
                        else:
                            measure_ingredient_ids.append(int(sql_check[0][0]))
                    if len(measure_ingredient_ids) == 2:
                        quantities.append((int(ingred_quant_measure[0]), measure_ingredient_ids))

            blog_database.insert_data(recipes, "recipes")
            blog_database.insert_data(quantities, "quantity")

        else:
            print("Error! Cannot create the database connection.")


if __name__ == "__main__":
    main()
