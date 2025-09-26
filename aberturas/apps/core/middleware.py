import logging
import time
from django.db import connection
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('transactions')

class TransactionLoggerMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request._start_time = time.time()
        request._queries_before = len(connection.queries)
        
    def process_response(self, request, response):
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            queries_count = len(connection.queries) - getattr(request, '_queries_before', 0)
            
            # Log de la transacción HTTP
            logger.info(
                f"🌐 {request.method} {request.path} | "
                f"Status: {response.status_code} | "
                f"Tiempo: {duration:.3f}s | "
                f"Queries: {queries_count} | "
                f"Usuario: {getattr(request.user, 'username', 'Anónimo')}"
            )
            
            # Log detallado de queries SQL si hay transacciones
            if queries_count > 0:
                for query in connection.queries[-queries_count:]:
                    sql = query['sql']
                    time_taken = query['time']
                    
                    # Detectar tipo de operación
                    operation = "📖 SELECT"
                    if sql.upper().startswith('INSERT'):
                        operation = "➕ INSERT"
                    elif sql.upper().startswith('UPDATE'):
                        operation = "✏️ UPDATE"
                    elif sql.upper().startswith('DELETE'):
                        operation = "🗑️ DELETE"
                    
                    logger.info(
                        f"  {operation} | Tiempo: {time_taken}s | "
                        f"SQL: {sql[:100]}{'...' if len(sql) > 100 else ''}"
                    )
        
        return response