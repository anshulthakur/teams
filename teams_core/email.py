from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_html_email(subject, to_email, context):
    # Render the plain text content
    text_content = render_to_string('mail/base.txt', context)
    # Render the HTML content
    html_content = render_to_string('mail/base.html', context)

    # Create the email
    email = EmailMultiAlternatives(subject, text_content, 'teamsadmin@cdot.in', [to_email])
    email.attach_alternative(html_content, "text/html")
    email.send()