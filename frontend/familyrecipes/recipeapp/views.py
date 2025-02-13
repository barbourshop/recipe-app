from django.shortcuts import render
from .models import Recipes

def recipe_list(request):
    recipeList = Recipes.objects.all()
    return render(request, 'recipe_list.html', {'recipes': recipeList})
