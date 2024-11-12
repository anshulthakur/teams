from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import TestCase, Subscription
from django.contrib.auth.models import User
from .utils import add_subscription, remove_subscription

@receiver(m2m_changed, sender=TestCase.maintainers.through)
def manage_subscriptions(sender, instance, action, pk_set, **kwargs):
    """
    Manage subscriptions when maintainers are added or removed.
    """
    if action == "post_add":
        for user_id in pk_set:
            user = User.objects.get(pk=user_id)
            add_subscription(user, 'TEST_EXECUTION_FAIL', instance)
    elif action == "post_remove":
        for user_id in pk_set:
            user = User.objects.get(pk=user_id)
            remove_subscription(user, 'TEST_EXECUTION_FAIL', instance)
    elif action == "post_clear":
        # Remove all subscriptions related to this TestCase for TEST_EXECUTION_FAIL
        Subscription.objects.filter(
            event_type='TEST_EXECUTION_FAIL',
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.id,
            user__in=instance.maintainers.all()
        ).update(active=False)

@receiver(post_save, sender=TestCase)
def subscribe_author_on_create(sender, instance, created, **kwargs):
    """
    Subscribe the author to TEST_EXECUTION_FAIL notifications when a TestCase is created.
    """
    if created and instance.author:
        add_subscription(instance.author, 'TEST_EXECUTION_FAIL', instance)
