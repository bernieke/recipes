from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static

from . import views


urlpatterns = [
    path('autocomplete/tag/', views.TagAutoComplete.as_view(),
         name='autocomplete-tag'),
    path('autocomplete/ingredient/', views.IngredientAutoComplete.as_view(),
         name='autocomplete-ingredient'),
    path('markdown/', include('django_markdown.urls')),
]
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('tag/<int:pk>/', views.tag, name='tag'),
    path('recipe/<int:pk>/', views.recipe, name='recipe'),
    path('cart/', views.cart, name='cart'),
    path('cart/add/<str:pk>/', views.add_to_cart, name='add_to_cart'),
)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
