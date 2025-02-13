import mysql.connector
import json
import os
import argparse 
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def insert_recipe(json_data, mydb):  # mydb is your database connection object

    try:
        mycursor = mydb.cursor()

        # Insert into recipes table
        recipe_title = recipe_data['title']
        recipe_description = recipe_data.get('description', None) # Handle missing fields
        recipe_instructions = recipe_data['instructions']
        recipe_prep_time = recipe_data.get('prep_time', None)
        recipe_cook_time = recipe_data.get('cook_time', None)
        recipe_servings = recipe_data.get('servings', None)

        sql = "INSERT INTO recipes (title, description, instructions, prep_time, cook_time, servings) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (recipe_title, recipe_description, recipe_instructions, recipe_prep_time, recipe_cook_time, recipe_servings)
        mycursor.execute(sql, val)
        mydb.commit()  # Important: Commit the changes

        recipe_id = mycursor.lastrowid  # Get the ID of the newly inserted recipe

        # Insert into ingredients and recipe_ingredients tables
        ingredients = recipe_data.get('ingredients', []) # Handle missing ingredients

        for ingredient_data in ingredients:
            ingredient_name = ingredient_data['name']
            quantity = ingredient_data['quantity']

            # Check if ingredient exists
            mycursor.execute("SELECT id FROM ingredients WHERE name = %s", (ingredient_name,))
            existing_ingredient = mycursor.fetchone()

            if existing_ingredient:
                ingredient_id = existing_ingredient[0]
            else:
                # Insert new ingredient
                mycursor.execute("INSERT INTO ingredients (name) VALUES (%s)", (ingredient_name,))
                mydb.commit()
                ingredient_id = mycursor.lastrowid

            # Insert into recipe_ingredients
            sql = "INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity) VALUES (%s, %s, %s)"
            val = (recipe_id, ingredient_id, quantity)
            mycursor.execute(sql, val)

        mydb.commit()  # Commit the ingredient/recipe_ingredient inserts
        print("Recipe inserted successfully!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        mydb.rollback()  # Rollback on error

# Get database credentials from environment variables
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


if not all([DB_HOST, DB_USER, DB_PASSWORD, DB_NAME]):
    raise ValueError("Missing database credentials in .env file.")

try:
    mydb = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    # --- Command-line argument parsing ---
    parser = argparse.ArgumentParser(description="Insert or modify a recipe from a JSON file.")
    parser.add_argument("json_file", help="Path to the JSON file.")
    args = parser.parse_args()

    json_file_path = args.json_file

    try:
        with open(json_file_path, "r") as f:
            recipe_data = json.load(f)  # Correct: Use json.load()

    except FileNotFoundError:
        raise FileNotFoundError(f"JSON file not found at {json_file_path}")
    except json.JSONDecodeError:
        raise json.JSONDecodeError(f"Invalid JSON in {json_file_path}")

    insert_recipe(recipe_data, mydb)

    # To delete:
    # modify_recipe(recipe_to_modify, {}, mydb, delete=True) # Empty new_recipe_data for delete

    mydb.close()

except mysql.connector.Error as err:
    print(f"Database connection error: {err}")
except ValueError as err:
    print(err)
except FileNotFoundError as err:
    print(err)
except json.JSONDecodeError as err:
    print(err)
except Exception as err:
    print(f"An unexpected error occurred: {err}")