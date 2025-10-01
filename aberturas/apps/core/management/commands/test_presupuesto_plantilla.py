from django.core.management.base import BaseCommand
from apps.sales.models import Presupuesto, LineaPresupuesto
from apps.catalog.models import ProductTemplate
from apps.crm.models import Cliente
from apps.accounts.models import User

class Command(BaseCommand):
    help = 'Prueba el sistema de presupuestos con plantillas'

    def handle(self, *args, **options):
        # Crear cliente de prueba
        cliente, created = Cliente.objects.get_or_create(
            code='TEST001',
            defaults={
                'name': 'Cliente de Prueba',
                'type': 'EMPRESA',
                'email': 'test@example.com'
            }
        )
        
        if created:
            self.stdout.write("✅ Cliente de prueba creado")
        
        # Obtener usuario
        user = User.objects.first()
        if not user:
            self.stdout.write("❌ No hay usuarios en el sistema")
            return
        
        # Crear presupuesto
        presupuesto = Presupuesto.objects.create(
            customer=cliente,
            created_by=user,
            description='Presupuesto de prueba con plantillas'
        )
        
        self.stdout.write(f"✅ Presupuesto creado: {presupuesto.number}")
        
        # Obtener plantilla
        template = ProductTemplate.objects.first()
        if not template:
            self.stdout.write("❌ No hay plantillas en el sistema")
            return
        
        # Configuración de ejemplo
        config_ejemplo = {
            'linea': 'A30',
            'marco': '45',
            'hoja': '54',
            'interior': '75',
            'dim': {
                'width_mm': 1200,
                'height_mm': 1500
            },
            'cantidad': 2,
            'mosquitero': True
        }
        
        # Crear línea de presupuesto
        linea = LineaPresupuesto.objects.create(
            quote=presupuesto,
            template=template,
            template_config=config_ejemplo,
            quantity=2
        )
        
        self.stdout.write(f"✅ Línea creada: {linea.description}")
        self.stdout.write(f"   Precio unitario: ${linea.unit_price}")
        self.stdout.write(f"   Total línea: ${linea.total}")
        
        # Mostrar totales del presupuesto
        self.stdout.write(f"\n📊 TOTALES DEL PRESUPUESTO:")
        self.stdout.write(f"   Subtotal: ${presupuesto.subtotal}")
        self.stdout.write(f"   IVA: ${presupuesto.tax_amount}")
        self.stdout.write(f"   Total: ${presupuesto.total}")
        
        # Mostrar configuración guardada
        self.stdout.write(f"\n🔧 CONFIGURACIÓN GUARDADA:")
        for key, value in linea.template_config.items():
            self.stdout.write(f"   {key}: {value}")
        
        self.stdout.write(f"\n🎯 Presupuesto ID: {presupuesto.id}")
        self.stdout.write("✅ Prueba completada exitosamente")