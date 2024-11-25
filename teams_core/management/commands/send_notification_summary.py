from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.mail import send_mail
from django.db.models import Count
from notifications.models import Notification
from django.urls import reverse
from django.conf import settings

from datetime import timedelta
from urllib.parse import urljoin

class Command(BaseCommand):
    help = "Send a summary email for notification updates to subscribed users."

    def handle(self, *args, **kwargs):
        # Calculate the last sent time (adjust this to your desired frequency)
        last_sent_time = timezone.now() - timedelta(days=1)
        
        # Retrieve all users who have unread notifications
        users_with_notifications = User.objects.filter(
            #notifications__timestamp__gte=last_sent_time,
            notifications__unread=True
        ).distinct()

        #print(f'Number of users for notifications: {len(users_with_notifications)}')

        for user in users_with_notifications:
            # Filter only relevant notifications for each user
            unread_notifications = user.notifications.filter(
                unread=True,
                #timestamp__gte=last_sent_time
            )

            # Calculate the failure count and find most frequently failing tests
            failure_count = unread_notifications.count()
            top_failing_tests = (
                unread_notifications
                .values('actor_object_id')  # Assume `actor_object_id` is your test case ID
                .annotate(count=Count('id'))
                .order_by('-count')[:5]
            )
            
            # Compose email content
            uname = user.get_short_name()
            if ((not uname) or  (uname and len(uname)==0)):
                uname = user.get_username()
            message = (
                f"Hello {uname},\n\n"
                f"Here is your test failure summary since the last email:\n"
                f"- Total new failures: {failure_count}\n"
            )
            
            if top_failing_tests:
                message += "\nTop failing tests:\n"
                for test in top_failing_tests:
                    test_id = test['actor_object_id']
                    count = test['count']
                    #test_url = f"https://example.com/test-case/{test_id}/"
                    test_url = urljoin(settings.TEAMS_HOST_URL, reverse('teams_core:test_case_detail', args=[test_id]))
                    message += f"- Test ID: {test_id} (Failures: {count}) - {test_url}\n"
            else:
                message += "\nNo tests failed recently.\n"

            #print(message)
            # Send email to user if they have any failures
            send_mail(
                subject="Test Failure Summary Notification",
                message=message,
                from_email=settings.TEAMS_ADMIN_MAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS(f"Sent summary email to {user.username}"))
