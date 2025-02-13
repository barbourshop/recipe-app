from django.shortcuts import render
from .models import Recipes, Ingredients

def recipe_list(request):
    recipes = Recipes.objects.all()
    # Get all ingredients for the dropdown
    ingredients = Ingredients.objects.all()
    print(f"Found {ingredients.count()} ingredients")
    print("Ingredients:", list(ingredients.values_list('name', flat=True)))
    
    
    # Handle recipe name search
    recipe_query = request.GET.get('q')
    if recipe_query:
        recipes = recipes.filter(title__icontains=recipe_query)
    
    # Handle ingredient search
    ingredient_query = request.GET.get('ingredient')
    if ingredient_query:
        recipes = recipes.filter(recipeingredients__ingredient__name__icontains=ingredient_query)
    
    return render(request, 'recipe_list.html', {
        'recipes': recipes,
        'ingredients': ingredients,
    })