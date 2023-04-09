import sqlite3
import sys
from sqlite3 import Error


def create_connection(db_file):
    """Create a connection to SQLite file"""
    conn = None

    try:
        conn = sqlite3.connect(db_file)
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
            for name, descript in data.items():
                c.execute(
                    f"INSERT INTO "
                    f"{table_name} ({table_name[:-1] + '_name'}, {table_name[:-1] + '_description'}) VALUES (?, ?);",
                    (name, descript))
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
    recipes = {}

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

    # create a database connection
    conn = create_connection(database)

    # create table
    if conn is not None:
        # create meals, ingredients, measures, recipes tables
        create_table(conn, sql_create_meals_table)
        create_table(conn, sql_create_ingredients_table)
        create_table(conn, sql_create_measures_table)
        create_table(conn, sql_create_recipes_table)

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
                recipes[recipe_name] = recipe_description

        insert_data(conn, recipes, "recipes")

        # close database connection
        conn.close()

    else:
        print("Error! Cannot create the database connection.")


if __name__ == "__main__":
    main()
