import mysql.connector
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def modify_recipe(recipe_title, new_recipe_data, mydb, delete=False):
    try:
        mycursor = mydb.cursor()

        # 1. Get the recipe ID
        sql = "SELECT id FROM recipes WHERE title = %s"
        val = (recipe_title,)
        mycursor.execute(sql, val)
        result = mycursor.fetchone()

        if result is None:
            print(f"Recipe '{recipe_title}' not found.")
            return

        recipe_id = result[0]

        if delete:
            # 2. Delete from recipe_ingredients
            sql = "DELETE FROM recipe_ingredients WHERE recipe_id = %s"
            val = (recipe_id,)
            mycursor.execute(sql, val)
            mydb.commit()

            # 3. Delete from recipes
            sql = "DELETE FROM recipes WHERE id = %s"
            val = (recipe_id,)
            mycursor.execute(sql, val)
            mydb.commit()

            print(f"Recipe '{recipe_title}' deleted successfully.")
            return  # Exit after deletion

        # 2. Modify recipe (if not deleting)
        sql_update_parts = []
        val_update = []

        if 'title' in new_recipe_data:
            sql_update_parts.append("title = %s")
            val_update.append(new_recipe_data['title'])
        if 'description' in new_recipe_data:
            sql_update_parts.append("description = %s")
            val_update.append(new_recipe_data['description'])
        if 'instructions' in new_recipe_data:
            sql_update_parts.append("instructions = %s")
            val_update.append(new_recipe_data['instructions'])
        if 'prep_time' in new_recipe_data:
            sql_update_parts.append("prep_time = %s")
            val_update.append(new_recipe_data['prep_time'])
        if 'cook_time' in new_recipe_data:
            sql_update_parts.append("cook_time = %s")
            val_update.append(new_recipe_data['cook_time'])
        if 'servings' in new_recipe_data:
            sql_update_parts.append("servings = %s")
            val_update.append(new_recipe_data['servings'])

        if sql_update_parts:  # Check if there are any updates
            sql = f"UPDATE recipes SET {', '.join(sql_update_parts)} WHERE id = %s"
            val_update.append(recipe_id)
            mycursor.execute(sql, tuple(val_update))
            mydb.commit()

        # 3. Modify ingredients (replace existing ingredients)
        if 'ingredients' in new_recipe_data:
            # First, delete existing ingredients for the recipe
            sql = "DELETE FROM recipe_ingredients WHERE recipe_id = %s"
            val = (recipe_id,)
            mycursor.execute(sql, val)
            mydb.commit()

            # Then, insert the new ingredients
            for ingredient_data in new_recipe_data['ingredients']:
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
            mydb.commit()

        print(f"Recipe '{recipe_title}' modified successfully.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        mydb.rollback()

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


    recipe_to_modify = "REPLACEME"  # Replace with the actual recipe title

    # New data for the recipe (can include any or all fields)
    new_recipe_data = {
        "title": "Modified Recipe Title for cookies",
        "description": "Even Better description",
        "prep_time": 25,
        "ingredients": [
            {"name": "New Ingredient 1", "quantity": "3 cups"},
            {"name": "New Ingredient 2", "quantity": "2 tbsp"}
        ]
    }

    # To modify:
    #modify_recipe(recipe_to_modify, new_recipe_data, mydb)

    # To delete:
    modify_recipe(recipe_to_modify, {}, mydb, delete=True) # Empty new_recipe_data for delete

    mydb.close()

except mysql.connector.Error as err:
    print(f"Database connection error: {err}")
except ValueError as err:
    print(err) # print the error for missing .env variables
except Exception as err:
    print(f"An unexpected error occurred: {err}")