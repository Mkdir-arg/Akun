import logging
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from apps.crm.models import Customer, Address
from apps.catalog.models import Product, PriceList, PriceListRule

logger = logging.getLogger('transactions')
User = get_user_model()

@receiver(post_save, sender=Customer)
def log_customer_save(sender, instance, created, **kwargs):
    action = "🆕 CREADO" if created else "📝 ACTUALIZADO"
    logger.info(f"💼 Cliente {action}: {instance.code} - {instance.name}")

@receiver(post_delete, sender=Customer)
def log_customer_delete(sender, instance, **kwargs):
    logger.info(f"🗑️ Cliente ELIMINADO: {instance.code} - {instance.name}")

@receiver(post_save, sender=Product)
def log_product_save(sender, instance, created, **kwargs):
    action = "🆕 CREADO" if created else "📝 ACTUALIZADO"
    logger.info(f"📦 Producto {action}: {instance.sku} - {instance.name}")

@receiver(post_delete, sender=Product)
def log_product_delete(sender, instance, **kwargs):
    logger.info(f"🗑️ Producto ELIMINADO: {instance.sku} - {instance.name}")

@receiver(post_save, sender=PriceList)
def log_pricelist_save(sender, instance, created, **kwargs):
    action = "🆕 CREADA" if created else "📝 ACTUALIZADA"
    logger.info(f"💰 Lista de Precios {action}: {instance.name}")

@receiver(post_save, sender=User)
def log_user_activity(sender, instance, created, **kwargs):
    if created:
        logger.info(f"👤 Usuario REGISTRADO: {instance.username}")
    else:
        logger.info(f"👤 Usuario ACTUALIZADO: {instance.username}")