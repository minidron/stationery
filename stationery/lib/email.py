from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags


def create_email(subject, body_html, to_email, body_txt=None, from_email=None,
                 **kwargs):
    """
    Создаём e-mail. Если не передать текстовую версию, то она автоматически
    создатся из html версии. По умолчанию адрес отправки берется из настроек.
    """
    if not body_txt:
        body_txt = ' '.join(strip_tags(body_html).split())
    if not from_email:
        from_email = settings.DEFAULT_FROM_EMAIL
    if not isinstance(to_email, list):
        to_email = [to_email]

    email = EmailMultiAlternatives(subject, body_txt, from_email, to_email,
                                   **kwargs)
    email.attach_alternative(body_html, 'text/html')

    return email
