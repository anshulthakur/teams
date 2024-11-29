from django.db.models.signals import m2m_changed, post_save, pre_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import TestCase, Subscription, TestSuite
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

@receiver(m2m_changed, sender=TestSuite.testcase_set.through)
def handle_test_suite_test_case_add(sender, instance, action, pk_set, **kwargs):
    """
    Handle subscriptions when TestCases are added to a TestSuite.
    """
    if action == "post_add":
        case_type = ContentType.objects.get_for_model(TestCase)
        suite_subscribers = Subscription.objects.filter(
            event_type="TEST_EXECUTION_FAIL",
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.id,
            active=True
        ).values_list("user", flat=True)

        for test_case_id in pk_set:
            for user_id in suite_subscribers:
                Subscription.objects.get_or_create(
                    user_id=user_id,
                    content_type=case_type,
                    object_id=test_case_id,
                    event_type="TEST_EXECUTION_FAIL"
                )

@receiver(pre_save, sender=TestCase)
def track_author_change(sender, instance, **kwargs):
    """
    Track changes to the author of a TestCase and manage subscriptions accordingly.
    """
    if instance.pk:  # Only for updates, not creation
        old_author = sender.objects.filter(pk=instance.pk).values_list('author', flat=True).first()
        if old_author and old_author != instance.author_id:
            # Remove subscription for the old author
            old_user = User.objects.get(pk=old_author)
            remove_subscription(old_user, 'TEST_EXECUTION_FAIL', instance)

@receiver(post_save, sender=TestCase)
def subscribe_author_on_create_or_update(sender, instance, created, **kwargs):
    """
    Subscribe the author to TEST_EXECUTION_FAIL notifications when a TestCase is created or updated.
    """
    if instance.author:
        add_subscription(instance.author, 'TEST_EXECUTION_FAIL', instance)