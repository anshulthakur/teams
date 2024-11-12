from django.contrib.contenttypes.models import ContentType
from teams_core.models import Subscription
from django.contrib.auth.models import User
from .models import Subscription, TestCase, TestSuite

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
    
    # If subscribing to a TestSuite, subscribe to all its TestCases
    if isinstance(obj, TestSuite):
        case_type = ContentType.objects.get_for_model(TestCase)
        for test_case in obj.testcase_set.all():
            Subscription.objects.get_or_create(
                user=user,
                content_type=case_type,
                object_id=test_case.id,
                event_type=event_type
            )
    return subscription


def remove_subscription(user, event_type, obj):
    """
    Deactivate a subscription if it exists.
    """
    content_type = ContentType.objects.get_for_model(obj)
    Subscription.objects.filter(
        user=user,
        event_type=event_type,
        content_type=content_type,
        object_id=obj.id
    ).update(active=False)

    # If unsubscribing from a TestSuite, remove subscriptions for all its TestCases
    if isinstance(obj, TestSuite):
        case_type = ContentType.objects.get_for_model(TestCase)
        Subscription.objects.filter(
            user=user,
            content_type=case_type,
            object_id__in=obj.testcase_set.values_list('id', flat=True),
            event_type=event_type
        ).delete()

def get_active_subscribers(event_type, obj):
    """Retrieve all active subscribers to a specific event for an object."""
    content_type = ContentType.objects.get_for_model(obj)
    return User.objects.filter(
        subscriptions__event_type=event_type,
        subscriptions__content_type=content_type,
        subscriptions__object_id=obj.id,
        subscriptions__active=True
    )
