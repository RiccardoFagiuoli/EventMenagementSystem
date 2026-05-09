from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Filtro personalizzato: recupera un valore da un dizionario usando una chiave."""
    if dictionary is None:
        return None
    return dictionary.get(key)