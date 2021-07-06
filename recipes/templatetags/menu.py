from django import template


register = template.Library()


@register.simple_tag
def get_menu_note(menu, day, meal):
    return getattr(menu, '_'.join([day, meal, 'note']), '')


@register.simple_tag
def get_menu_dishes(menu, day, meal):
    try:
        return menu.list(day, meal)
    except AttributeError:
        return []
