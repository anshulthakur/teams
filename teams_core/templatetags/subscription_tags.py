# Inside yourapp/templatetags/subscription_tags.py
from django import template
from django.contrib.contenttypes.models import ContentType
from teams_core.models import Subscription

register = template.Library()

@register.filter
def is_subscribed(user, obj):
    """Check if the user is subscribed to an event for a specific object."""
    content_type = ContentType.objects.get_for_model(obj)
    return Subscription.objects.filter(
        user=user,
        content_type=content_type,
        object_id=obj.id,
        event_type='TEST_EXECUTION_FAIL',
        active=True
    ).exists()

@register.filter
def model_name(value):
    return ContentType.objects.get_for_model(value).model
