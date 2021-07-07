from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static

from . import views


urlpatterns = [
    path('autocomplete/tag/', views.TagAutoComplete.as_view(),
         name='autocomplete-tag'),
    path('autocomplete/ingredient/', views.IngredientAutoComplete.as_view(),
         name='autocomplete-ingredient'),
    path('martor/', include('martor.urls')),
]
urlpatterns += i18n_patterns(
    url(r'^login/$', views.login, name='account_login'),
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('tag/<int:pk>/', views.tag, name='tag'),
    path('recipe/<int:pk>/', views.recipe, name='recipe'),
    path('recipe/<int:pk>/<str:qty>', views.recipe_qty, name='recipe-qty'),
    path('cart/', views.cart, name='cart'),
    path('cart/add/<str:pk>/<str:qty>', views.add_to_cart, name='add_to_cart'),
    path('cart/del/<str:pk>/', views.del_from_cart, name='del_from_cart'),
    path('menu/', views.menu_today, name='menu_today'),
    path('menu/add/', views.add_to_dishes, name='add_to_dishes'),
    path('menu/del/', views.del_from_dishes, name='del_from_dishes'),
    path('menu/<int:year>/<int:week>/', views.menu, name='menu'),
    path('menu/<int:year>/<int:week>/<str:day>/<str:meal>/add/',
         views.add_to_menu, name='add_to_menu'),
    path('menu/<int:year>/<int:week>/<str:day>/<str:meal>/del/',
         views.del_from_menu, name='del_from_menu'),
    path('menu/<int:year>/<int:week>/<str:day>/<str:meal>/note/',
         views.change_note, name='change_note'),
)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
