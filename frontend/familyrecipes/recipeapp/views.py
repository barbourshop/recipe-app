from django.shortcuts import render
from .models import Recipes

def recipe_list(request):
    recipes = Recipes.objects.all()
    
    # Handle recipe name search
    recipe_query = request.GET.get('q')
    if recipe_query:
        recipes = recipes.filter(title__icontains=recipe_query)
    
    # Handle ingredient search
    ingredient_query = request.GET.get('ingredient')
    if ingredient_query:
        recipes = recipes.filter(ingredients__name__icontains=ingredient_query)
    
    return render(request, 'recipe_list.html', {'recipes': recipes})