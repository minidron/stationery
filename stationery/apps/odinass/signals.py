from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from odinass.documents import OfferDocType, CategoryDocType
from odinass.models import Offer, Product, Category


@receiver(post_save, sender=Product)
def update_product_offer_index(sender, instance, **kwargs):
    OfferDocType().update(instance.offers.all())


@receiver(post_delete, sender=Product)
def delete_product_offer_index(sender, instance, **kwargs):
    OfferDocType().update(instance.offers.all(), action='delete')


@receiver(post_save, sender=Offer)
def update_offer_index(sender, instance, **kwargs):
    OfferDocType().update(instance)


@receiver(post_delete, sender=Offer)
def delete_offer_index(sender, instance, **kwargs):
    OfferDocType().update(instance, action='delete')


@receiver(post_save, sender=Category)
def update_category_index(sender, instance, **kwargs):
    OfferDocType().update(instance.offers())
    CategoryDocType().update(instance)


@receiver(post_delete, sender=Category)
def delete_category_index(sender, instance, **kwargs):
    OfferDocType().update(Offer.objects.filter(product__category=instance),
                          action='delete')
    CategoryDocType().update(instance, action='delete')
