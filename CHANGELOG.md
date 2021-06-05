3.6.4
=====
* Add search field to recipes admin page
* Add menu templates and menu per week

3.6.3
=====
* Fix markdownify settings change

3.6.2
=====
* Fix OurGroceries import

3.6.1
=====
* Add subsort on lowercased title

3.6
===
* Fix bug with django-markdown on Django 2.2
* Add a little whitespace at the bottom of the page
* Add "all" tag
* Add option to sort by either popularity or title

3.5.1
=====
* Fix for OurGroceries API change

3.5
===
* Add popularity as number of times a recipe was added to ourgroceries
* Use popularity as first sort before recipe title
* Remember ingredient selection in shopping list when login is required

3.4
===
* Prevent overwriting changes to the week menu
* Reduce size of titles on recipe page

3.3
===
* Fix unit conversions
* Expand unit conversion lookups

3.2
===
* Fix change quantity
* Mark current day on the week menu

3.1
===
* Put lunch and dinner in columns

3.0
===
* Swap ingredients and recipes columns on shopping list page
* Increase size of title and tags fields on recipe admin
* Don't send to OurGroceries when DEBUG is active
* Add week menu page

2.6
===
* Fix add to ourgroceries

2.5
===
* Add search on name and alias to admin ingredient list
* Add alias to admin ingredient list
* Fix ingredient name for aliases in admin dropdown
* Generate ingredient display name for use on recipe and cart pages
* Allow for reverse unit conversion
* Allow for unit conversion through ingredient units

2.4
===
* Fix adding non-primary unit ingredient to shopping cart.

2.3
===
* Fix adding new ingredient.
* Fix grab_production.sh
* Pin django-autocomplete-light until the jquery loading order issue is fixed.

2.2
===
* Update translations.
* Show primary unit bold on ingredient admin list display.

2.1
===
* Add the admin pages for categories and units back.

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

2.0
===
* Add ingredient units.
* Make ingredient names unique.
* Group shopping cart ingredients by primary unit.
* Add links to recipes on ingredient and tag admin pages.
* Remove admin pages for categories and units.

1.6
===
* Fix cart button on recipe page.

1.5
===
* Fix layout discrepancy between recipe and index/cart.
* Increase tag/ingredient column size.
* Change tag font size on recipe page to match ingredients.

1.4
===
* Add delete button to shopping cart.
* Add tag list to recipes admin list view.
* Allow cart quantities differing from the 0.5 step.

1.3
===
* Add read-only list of recipes to ingredient admin page.

1.2
===
* Change tag break to same height as tag so it will match up with the recipe list entries.
* Only show tags which have recipes.
* Add tags to recipe page.
* Add break_after to tag admin list display.
* Add category to ingredient admin list display.

1.1
===
When adding an ingredient to a recipe the unit now defaults to empty. Leaving it empty will make it use the ingredient unit.

1.0
===
Inital release.
