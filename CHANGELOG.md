1.0
===
Inital release.

1.1
===
When adding an ingredient to a recipe the unit now defaults to empty. Leaving it empty will make it use the ingredient unit.

1.2
===
* Change tag break to same height as tag so it will match up with the recipe list entries.
* Only show tags which have recipes.
* Add tags to recipe page.
* Add break_after to tag admin list display.
* Add category to ingredient admin list display.

1.3
===
* Add read-only list of recipes to ingredient admin page.

1.4
===
* Add delete button to shopping cart.
* Add tag list to recipes admin list view.
* Allow cart quantities differing from the 0.5 step.

1.5
===
* Fix layout discrepancy between recipe and index/cart.
* Increase tag/ingredient column size.
* Change tag font size on recipe page to match ingredients.

1.6
===
* Fix cart button on recipe page.

2.0
===
* Add ingredient units.
* Make ingredient names unique.
* Group shopping cart ingredients by primary unit.
* Add links to recipes on ingredient and tag admin pages.
* Remove admin pages for categories and units.

NOTE:
All duplicate ingredient names will be merged. Their different units will now be ingredient units.
You will need to choose a primary unit on the ingredient admin page for all ingredients which had duplicate names, and add conversion factors to the non-primary ingredient units.
Run following command to get a list of all these ingredients:
```
./manage.py shell -c "
from recipes.models import Ingredient
from django.db.models import Count
print('\n'.join(Ingredient.objects
                .all()
                .annotate(units=Count('ingredientunit'))
                .filter(units__gt=1).values_list('name', flat=True)))"
```

2.1
===
* Add the admin pages for categories and units back.
