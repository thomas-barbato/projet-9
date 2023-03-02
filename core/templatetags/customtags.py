from django import template

register = template.Library()


@register.filter(name="loop")
def loop(number, start_step=0):
    return range(int(start_step), number)
