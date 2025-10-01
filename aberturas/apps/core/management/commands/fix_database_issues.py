from django.core.management.base import BaseCommand
from django.db import connection, transaction

class Command(BaseCommand):
    help = 'Corrige errores críticos en la base de datos (renombra tablas con espacios)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo muestra qué cambios se harían sin ejecutarlos',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Ejecuta los cambios sin confirmación',
        )

    def handle(self, *args, **options):
        # Mapeo de nombres de tablas: nombre_actual -> nombre_nuevo
        table_renames = {
            'tipo de accesorios': 'tipo_accesorios',
            'tipo de interiores': 'tipo_interiores', 
            'tipos colocación': 'tipos_colocacion',
            'contravidrio exterior': 'contravidrio_exterior',
            'vidrio repartido': 'vidrio_repartido',
            'gest_cuentas clientes': 'gest_cuentas_clientes',
            'gest_cuentas proveedores': 'gest_cuentas_proveedores',
            'gest_historial de obra': 'gest_historial_obra',
            'gest_ingreso de accesorios': 'gest_ingreso_accesorios',
            'gest_ingreso de perfiles': 'gest_ingreso_perfiles',
            'gest_ingreso de vidrios': 'gest_ingreso_vidrios',
            'gest_pedido de accesorios': 'gest_pedido_accesorios',
            'gest_pedido de perfiles': 'gest_pedido_perfiles',
            'gest_pedido de vidrios': 'gest_pedido_vidrios',
            'despiece accesorios contravidrio': 'despiece_accesorios_contravidrio',
            'despiece accesorios contravidrio exterior': 'despiece_accesorios_contravidrio_exterior',
            'despiece accesorios cruces': 'despiece_accesorios_cruces',
            'despiece accesorios hoja': 'despiece_accesorios_hoja',
            'despiece accesorios interior': 'despiece_accesorios_interior',
            'despiece accesorios marco': 'despiece_accesorios_marco',
            'despiece accesorios mosquitero': 'despiece_accesorios_mosquitero',
            'despiece accesorios vidrio repartido': 'despiece_accesorios_vidrio_repartido',
            'despiece cruces': 'despiece_cruces',
            'despiece interior': 'despiece_interior',
            'despiece interior mosquitero': 'despiece_interior_mosquitero',
            'despiece perfiles contravidrios': 'despiece_perfiles_contravidrios',
            'despiece perfiles contravidrios exterior': 'despiece_perfiles_contravidrios_exterior',
            'despiece perfiles hojas': 'despiece_perfiles_hojas',
            'despiece perfiles marcos': 'despiece_perfiles_marcos',
            'despiece perfiles mosquitero': 'despiece_perfiles_mosquitero',
            'despiece perfiles vidrio repartido': 'despiece_perfiles_vidrio_repartido',
            'encabezados y pies': 'encabezados_pies',
            'recortes de perfiles': 'recortes_perfiles',
        }

        with connection.cursor() as cursor:
            # Verificar qué tablas existen
            cursor.execute("SHOW TABLES")
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            tables_to_rename = []
            for old_name, new_name in table_renames.items():
                if old_name in existing_tables:
                    tables_to_rename.append((old_name, new_name))

            if not tables_to_rename:
                self.stdout.write(self.style.SUCCESS("✅ No hay tablas con espacios para renombrar"))
                return

            self.stdout.write(f"📋 Encontradas {len(tables_to_rename)} tablas para renombrar:")
            for old_name, new_name in tables_to_rename:
                self.stdout.write(f"  • {old_name} → {new_name}")

            if options['dry_run']:
                self.stdout.write(self.style.WARNING("\n🔍 MODO DRY-RUN: No se ejecutarán cambios"))
                return

            if not options['force']:
                confirm = input("\n¿Continuar con el renombrado? (y/N): ")
                if confirm.lower() != 'y':
                    self.stdout.write("❌ Operación cancelada")
                    return

            # Ejecutar renombrados
            self.stdout.write("\n🔄 Iniciando renombrado de tablas...")
            
            success_count = 0
            error_count = 0
            
            for old_name, new_name in tables_to_rename:
                try:
                    with transaction.atomic():
                        cursor.execute(f"ALTER TABLE `{old_name}` RENAME TO `{new_name}`")
                        self.stdout.write(f"  ✅ {old_name} → {new_name}")
                        success_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  ❌ Error renombrando {old_name}: {e}"))
                    error_count += 1

            # Crear índices básicos
            self.stdout.write("\n🔄 Creando índices básicos...")
            
            indices = [
                ("gest_clientes", "nombre", "idx_gest_clientes_nombre"),
                ("gest_obras", "id_cliente", "idx_gest_obras_cliente"),
                ("marco", "id_producto", "idx_marco_producto"),
                ("hoja", "id_marco", "idx_hoja_marco"),
                ("interior", "id_hoja", "idx_interior_hoja"),
            ]
            
            for table, column, index_name in indices:
                if table in existing_tables:
                    try:
                        cursor.execute(f"CREATE INDEX {index_name} ON `{table}`(`{column}`)")
                        self.stdout.write(f"  ✅ Índice {index_name} creado")
                    except Exception as e:
                        if "Duplicate key name" not in str(e):
                            self.stdout.write(f"  ⚠️  Índice {index_name}: {e}")

            # Resumen final
            self.stdout.write(f"\n📊 RESUMEN:")
            self.stdout.write(f"  • Tablas renombradas exitosamente: {success_count}")
            self.stdout.write(f"  • Errores: {error_count}")
            
            if error_count == 0:
                self.stdout.write(self.style.SUCCESS("\n🎉 ¡Corrección completada exitosamente!"))
            else:
                self.stdout.write(self.style.WARNING(f"\n⚠️  Completado con {error_count} errores"))

            # Verificación final
            self.stdout.write("\n🔍 Verificando tablas restantes con espacios...")
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_SCHEMA = 'akun' 
                AND TABLE_NAME LIKE '% %'
            """)
            
            remaining_tables = cursor.fetchall()
            if remaining_tables:
                self.stdout.write("⚠️  Tablas con espacios restantes:")
                for table in remaining_tables:
                    self.stdout.write(f"  • {table[0]}")
            else:
                self.stdout.write(self.style.SUCCESS("✅ No quedan tablas con espacios"))