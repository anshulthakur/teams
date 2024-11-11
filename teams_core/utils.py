from django.contrib.contenttypes.models import ContentType
from teams_core.models import Subscription
from django.contrib.auth.models import User

def add_subscription(user, event_type, obj):
    """Add or reactivate a subscription for a user to a specific event and object."""
    content_type = ContentType.objects.get_for_model(obj)
    subscription, created = Subscription.objects.get_or_create(
        user=user,
        event_type=event_type,
        content_type=content_type,
        object_id=obj.id
    )
    if not created and not subscription.active:
        subscription.active = True
        subscription.save()
    return subscription

def toggle_subscription(user, event_type, obj):
    """Toggle subscription status for a specific event and object."""
    content_type = ContentType.objects.get_for_model(obj)
    subscription = Subscription.objects.filter(
        user=user,
        event_type=event_type,
        content_type=content_type,
        object_id=obj.id
    ).first()
    if subscription:
        subscription.active = not subscription.active
        subscription.save()

def get_active_subscribers(event_type, obj):
    """Retrieve all active subscribers to a specific event for an object."""
    content_type = ContentType.objects.get_for_model(obj)
    return User.objects.filter(
        subscriptions__event_type=event_type,
        subscriptions__content_type=content_type,
        subscriptions__object_id=obj.id,
        subscriptions__active=True
    )
