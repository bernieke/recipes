from django import template


register = template.Library()


@register.simple_tag
def get_menu_field(menu, day, meal, item):
    return getattr(menu, '_'.join([day, meal, item]))
