import sqlite3
from sqlite3 import Error


class Database:
    """Class with functions that operate with a database"""

    def __init__(self, db_file):
        self.db_file = db_file

    def __enter__(self):
        self.conn = self.create_connection(self.db_file)
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        self.conn.close()

    @staticmethod
    def create_connection(db_file):
        """Create a connection to SQLite file"""
        try:
            conn = sqlite3.connect(db_file)
            conn.execute("PRAGMA foreign_keys = ON")
            return conn
        except Error as e:
            print(e)
            return None

    def create_tables(self, create_table_sql_queries):
        """Create a table from the create_table_sql statement"""
        try:
            c = self.conn.cursor()
            for query in create_table_sql_queries:
                c.execute(query)
                self.conn.commit()
        except Error as e:
            print(e)

    def insert_data(self, data, table_name):
        """Populate tables from the insert_data_statement"""
        try:
            c = self.conn.cursor()
            if table_name == "recipes":
                for recipe in data:
                    c.execute(
                        f"INSERT INTO "
                        f"{table_name} ({table_name[:-1] + '_name'}, {table_name[:-1] + '_description'}) VALUES (?, ?);",
                        (recipe[0], recipe[1]))
                    self.conn.commit()
                    last_recipe_id = c.lastrowid
                    for meal in recipe[2]:
                        c.execute(f"INSERT INTO serve (meal_id, recipe_id) VALUES (?, ?)", (meal, last_recipe_id))
                        self.conn.commit()
            elif table_name == "quantity":
                for quantity in data:
                    c.execute("SELECT COUNT(*) FROM recipes")
                    last_rec_id = c.fetchone()
                    c.execute(
                        f"INSERT INTO quantity (quantity, recipe_id, measure_id, ingredient_id) VALUES (?, ?, ?, ?)",
                        (quantity[0], last_rec_id[0], quantity[1][0], quantity[1][1]))
                    self.conn.commit()
            else:
                for item in data:
                    c.execute(f"INSERT INTO {table_name} ({table_name[:-1] + '_name'}) VALUES (?);", (item,))
                self.conn.commit()
        except Error as e:
            print(e)

        self.conn.commit()
