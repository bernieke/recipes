from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('tag/<int:pk>/', views.tag, name='tag'),
    path('recipe/<int:pk>/', views.recipe, name='recipe'),
    path('cart/', views.cart, name='cart'),
    path('cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('autocomplete/tag/', views.TagAutoComplete.as_view(),
         name='autocomplete-tag'),
    path('autocomplete/ingredient/', views.IngredientAutoComplete.as_view(),
         name='autocomplete-ingredient'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
