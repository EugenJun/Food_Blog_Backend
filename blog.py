import sqlite3
import sys
from sqlite3 import Error


def create_connection(db_file):
    """Create a connection to SQLite file"""
    conn = None

    try:
        conn = sqlite3.connect(db_file)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    """Create a table from the create_table_sql statement"""
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
        conn.commit()
    except Error as e:
        print(e)


def insert_data(conn, data, table_name):
    """Populate tables from the insert_data_statement"""
    try:
        c = conn.cursor()
        if table_name == "recipes":
            for recipe in data:
                c.execute(
                    f"INSERT INTO "
                    f"{table_name} ({table_name[:-1] + '_name'}, {table_name[:-1] + '_description'}) VALUES (?, ?);",
                    (recipe[0], recipe[1]))
                conn.commit()
                sql_get_last_recipe_id = "SELECT * FROM recipes"
                last_recipe_id = conn.execute(sql_get_last_recipe_id).lastrowid
                for meal in recipe[2]:
                    c.execute(f"INSERT INTO serve (meal_id, recipe_id) VALUES (?, ?)", (meal, last_recipe_id))
                    conn.commit()
        else:
            for item in data:
                c.execute(f"INSERT INTO {table_name} ({table_name[:-1] + '_name'}) VALUES (?);", (item,))
            conn.commit()
    except Error as e:
        print(e)


def main():
    # user_input database name
    database = sys.argv[1]

    # data to populate tables
    data = {"meals": ("breakfast", "brunch", "lunch", "supper"),
            "ingredients": ("milk", "cacao", "strawberry", "blueberry", "blackberry", "sugar"),
            "measures": ("ml", "g", "l", "cup", "tbsp", "tsp", "dsp", "")}
    recipes = []

    # sqlite queries to create tables
    sql_create_meals_table = '''CREATE TABLE IF NOT EXISTS meals (
                                    meal_id INTEGER PRIMARY KEY,
                                    meal_name TEXT UNIQUE NOT NULL);'''
    sql_create_ingredients_table = '''CREATE TABLE IF NOT EXISTS ingredients (
                                        ingredient_id INTEGER PRIMARY KEY,
                                        ingredient_name TEXT UNIQUE NOT NULL);'''
    sql_create_measures_table = '''CREATE TABLE IF NOT EXISTS measures (
                                        measure_id INTEGER PRIMARY KEY,
                                        measure_name TEXT UNIQUE);'''
    sql_create_recipes_table = '''CREATE TABLE IF NOT EXISTS recipes (
                                        recipe_id INTEGER PRIMARY KEY,
                                        recipe_name TEXT NOT NULL,
                                        recipe_description TEXT);'''
    sql_create_serve_table = '''CREATE TABLE IF NOT EXISTS serve (
                                    serve_id INTEGER PRIMARY KEY,
                                    meal_id INTEGER NOT NULL,
                                    recipe_id INTEGER NOT NULL,
                                    FOREIGN KEY(meal_id) REFERENCES meals(meal_id),
                                    FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id));'''

    # create a database connection
    conn = create_connection(database)

    # create table
    if conn is not None:
        # create meals, ingredients, measures, recipes tables
        create_table(conn, sql_create_meals_table)
        create_table(conn, sql_create_ingredients_table)
        create_table(conn, sql_create_measures_table)
        create_table(conn, sql_create_recipes_table)
        create_table(conn, sql_create_serve_table)

        # insert data into tables meals, ingredients, measures
        insert_data(conn, data["meals"], "meals")
        insert_data(conn, data["ingredients"], "ingredients")
        insert_data(conn, data["measures"], "measures")

        # ask user for recipes
        print("Pass the empty recipe name to exit.")
        while True:
            recipe_name = input("Recipe name: ")
            if recipe_name == "":
                break
            else:
                recipe_description = input("Recipe description: ")
                sql_get_meals = "SELECT * FROM meals"
                meals = conn.execute(sql_get_meals)
                for meal in meals:
                    print(f"{meal[0]}) {meal[1]}", end=" ")
                meals_to_serve = list(map(int, input("When the dish can be served: ").split(" ")))
                recipes.append((recipe_name, recipe_description, meals_to_serve))

        insert_data(conn, recipes, "recipes")

        # close database connection
        conn.close()

    else:
        print("Error! Cannot create the database connection.")


if __name__ == "__main__":
    main()
