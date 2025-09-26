import time
import logging
from django.core.management.base import BaseCommand
from django.db import connection

logger = logging.getLogger('transactions')

class Command(BaseCommand):
    help = 'Monitor de transacciones en tiempo real'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=1,
            help='Intervalo en segundos para mostrar estadísticas (default: 1)'
        )
    
    def handle(self, *args, **options):
        interval = options['interval']
        
        self.stdout.write(
            self.style.SUCCESS('🚀 Monitor de transacciones iniciado')
        )
        self.stdout.write(f'📊 Mostrando estadísticas cada {interval} segundo(s)')
        self.stdout.write('=' * 60)
        
        last_query_count = len(connection.queries)
        
        try:
            while True:
                current_query_count = len(connection.queries)
                new_queries = current_query_count - last_query_count
                
                if new_queries > 0:
                    logger.info(f"📈 {new_queries} nueva(s) consulta(s) SQL ejecutada(s)")
                
                last_query_count = current_query_count
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('\n🛑 Monitor detenido por el usuario')
            )