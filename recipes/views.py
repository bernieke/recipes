from django.http import HttpResponse
# from django.shortcuts import render
from dal import autocomplete

from .models import Tag, Ingredient


def index(request):
    return HttpResponse('hello')


class TagAutoComplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        if self.q:
            return Tag.objects.filter(name__istartswith=self.q)
        else:
            return Tag.objects.all()


class IngredientAutoComplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        if self.q:
            return Ingredient.objects.filter(name__istartswith=self.q)
        else:
            return Ingredient.objects.all()
