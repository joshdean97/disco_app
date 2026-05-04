from django import template
from authentication.models import Staff, Operator

register = template.Library()

@register.filter
def is_operator(user):
    return Operator.objects.filter(user=user).exists()

@register.filter
def is_staffuser(user):
    return Staff.objects.filter(user=user).exists()
