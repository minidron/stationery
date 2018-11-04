import django.dispatch


payment_created = django.dispatch.Signal(providing_args=['instance'])
payment_done = django.dispatch.Signal(providing_args=['instance'])
