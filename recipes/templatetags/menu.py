from django import template


register = template.Library()


@register.simple_tag
def get_menu_field(form, day, meal, item):
    field_name = '_'.join([day, meal, item])
    return form.data.get(field_name, form.initial.get(field_name, ''))
