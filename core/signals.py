from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Product, User
from django.utils.text import slugify



@receiver(post_save, sender=Product)
def product_post_save(sender, instance, created, **kwargs):
    if created:
        instance.slug = slugify(instance.name + '-' + str(instance.id))
        instance.save()

@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    if created and instance.is_superuser:
        instance.role = None
        instance.save()