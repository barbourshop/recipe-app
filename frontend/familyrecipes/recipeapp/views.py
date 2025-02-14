from django.shortcuts import render, get_object_or_404
from .models import Recipes, Ingredients
from urllib.parse import urlencode

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

def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipes, pk=recipe_id)
    
    # Now we can use the cleaner 'ingredients' related name
    ingredients = recipe.ingredients.select_related('ingredient').all()
    
    search_params = urlencode({
        'q': request.GET.get('q', ''),
        'ingredient': request.GET.get('ingredient', '')
    })
    
    return render(request, 'recipe_detail.html', {
        'recipe': recipe,
        'ingredients': ingredients,
        'search_params': search_params,
    })