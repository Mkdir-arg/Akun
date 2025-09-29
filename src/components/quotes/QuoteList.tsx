import React, { useState, useEffect } from 'react';
import { Plus, Search, Filter, Eye, Edit, FileText, Send, X, CheckCircle } from 'lucide-react';

interface Quote {
  id: number;
  number: string;
  customer_name: string;
  status: string;
  priority: string;
  total: string;
  valid_until: string;
  created_at: string;
}

const QuoteList: React.FC = () => {
  const [quotes, setQuotes] = useState<Quote[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchQuotes();
  }, []);

  const fetchQuotes = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/quotes/`, {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        const quotesWithStatus = await Promise.all((data.results || data).map(async (quote: Quote) => {
          // Verificar si el presupuesto está vencido
          if (quote.valid_until && new Date(quote.valid_until) < new Date() && quote.status !== 'SOLD' && quote.status !== 'EXPIRED') {
            // Actualizar en la base de datos
            try {
              await fetch(`${process.env.REACT_APP_API_URL}/api/quotes/${quote.id}/`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ status: 'EXPIRED' })
              });
            } catch (error) {
              console.error('Error updating expired quote:', error);
            }
            return { ...quote, status: 'EXPIRED' };
          }
          return quote;
        }));
        setQuotes(quotesWithStatus);
      }
    } catch (error) {
      console.error('Error fetching quotes:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleConvertToSale = async (quote: Quote) => {
    if (window.confirm(`¿Estás seguro de convertir el presupuesto ${quote.number} a venta?`)) {
      try {
        const response = await fetch(`${process.env.REACT_APP_API_URL}/api/quotes/${quote.id}/`, {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify({
            status: 'SOLD'
          })
        });
        
        if (response.ok) {
          alert('Presupuesto convertido a venta exitosamente');
          fetchQuotes();
        } else {
          alert('Error al convertir el presupuesto a venta');
        }
      } catch (error) {
        console.error('Error converting to sale:', error);
        alert('Error al convertir el presupuesto a venta');
      }
    }
  };

  const handleSendQuote = async (quote: Quote) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/quotes/${quote.id}/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ status: 'SENT' })
      });

      if (response.ok) {
        fetchQuotes();
        alert('Presupuesto enviado exitosamente');
      }
    } catch (error) {
      console.error('Error sending quote:', error);
    }
  };

  const handleMarkAsRejected = async (quote: Quote) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/quotes/${quote.id}/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ status: 'REJECTED' })
      });

      if (response.ok) {
        fetchQuotes();
        alert('Presupuesto marcado como desestimado');
      }
    } catch (error) {
      console.error('Error marking as rejected:', error);
    }
  };

  const handleGeneratePDF = async (quote: Quote) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/quote-items/?quote=${quote.id}`, {
        credentials: 'include'
      });
      
      let items = [];
      if (response.ok) {
        const data = await response.json();
        items = data.results || data;
      }

      const currentDate = new Date().toLocaleDateString('es-AR');
      const validUntil = quote.valid_until ? new Date(quote.valid_until).toLocaleDateString('es-AR') : '';
      
      const htmlContent = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Presupuesto ${quote.number}</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: 'Arial', sans-serif; font-size: 12px; line-height: 1.4; color: #333; }
    .container { max-width: 800px; margin: 0 auto; padding: 20px; }
    
    .header { 
      background: linear-gradient(135deg, #e8eaf6 0%, #c5cae9 100%);
      padding: 30px 40px;
      margin-bottom: 30px;
      border-radius: 8px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .logo-section {
      display: flex;
      align-items: center;
    }
    
    .contact-info {
      text-align: right;
      color: #424242;
      font-size: 11px;
      line-height: 1.6;
    }
    
    .quote-info {
      display: flex;
      justify-content: space-between;
      margin-bottom: 30px;
      padding: 0 10px;
    }
    
    .customer-info, .quote-details {
      flex: 1;
    }
    
    .quote-details {
      text-align: right;
    }
    
    .info-row {
      margin-bottom: 8px;
      display: flex;
      align-items: center;
    }
    
    .info-label {
      font-weight: bold;
      margin-right: 10px;
      min-width: 120px;
      color: #555;
    }
    
    .conditions-section {
      display: flex;
      gap: 20px;
      margin: 25px 0;
      flex-wrap: wrap;
    }
    
    .condition-box {
      background: #bbdefb;
      padding: 8px 15px;
      border-radius: 4px;
      text-align: center;
      font-weight: bold;
      font-size: 10px;
      color: #1565c0;
    }
    
    .condition-content {
      flex: 1;
      text-align: center;
      padding: 8px;
      font-size: 11px;
      min-width: 120px;
    }
    
    .products-table {
      width: 100%;
      border-collapse: collapse;
      margin: 25px 0;
      border: 2px solid #1565c0;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .products-table th {
      background: #1565c0;
      color: white;
      padding: 12px 10px;
      text-align: center;
      font-weight: bold;
      font-size: 11px;
      border: 1px solid #0d47a1;
    }
    
    .products-table td {
      padding: 10px;
      border: 1px solid #ddd;
      font-size: 10px;
      vertical-align: top;
    }
    
    .products-table tbody tr:nth-child(even) {
      background-color: #f8f9fa;
    }
    
    .product-description {
      max-width: 300px;
      word-wrap: break-word;
      line-height: 1.3;
    }
    
    .product-name {
      font-weight: bold;
      color: #1565c0;
      margin-bottom: 3px;
    }
    
    .text-center { text-align: center; }
    .text-right { text-align: right; }
    
    .totals-section {
      margin-top: 30px;
      display: flex;
      justify-content: flex-end;
    }
    
    .totals-table {
      border-collapse: collapse;
      min-width: 280px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .totals-table td {
      padding: 10px 20px;
      border: 1px solid #ddd;
      font-size: 12px;
    }
    
    .totals-table .label {
      background: #f5f5f5;
      font-weight: bold;
      text-align: right;
      color: #555;
    }
    
    .totals-table .amount {
      text-align: right;
      background: white;
      font-weight: 500;
    }
    
    .total-row .label, .total-row .amount {
      background: #1565c0;
      color: white;
      font-weight: bold;
      font-size: 14px;
    }
    
    .footer {
      margin-top: 40px;
      padding-top: 20px;
      border-top: 2px solid #e0e0e0;
      text-align: center;
      font-size: 10px;
      color: #666;
    }
    
    @media print {
      body { margin: 0; }
      .container { padding: 10px; }
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="logo-section">
        <img src="http://localhost:3001/AKUN-LOGO.png" alt="AKUN ABERTURAS" style="height: 60px; width: auto; margin-right: 15px;" onerror="this.style.display='none'; this.nextElementSibling.style.display='block';" />
        <div class="logo-fallback" style="display: none;">
          <div style="font-size: 36px; font-weight: bold; color: #1565c0;">AKUN</div>
          <div style="font-size: 16px; color: #424242; letter-spacing: 2px;">ABERTURAS</div>
        </div>
      </div>
      <div class="contact-info">
        <div><strong>Teléfono:</strong> 11 44482992</div>
        <div><strong>Web:</strong> www.akunaberturas.com.ar</div>
        <div><strong>Email:</strong> akunaberturas@gmail.com</div>
      </div>
    </div>
    
    <div class="quote-info">
      <div class="customer-info">
        <div class="info-row">
          <span class="info-label">Para:</span>
          <span><strong>${quote.customer_name}</strong></span>
        </div>
        <div class="info-row">
          <span class="info-label">Presupuesto N°:</span>
          <span><strong>${quote.number}</strong></span>
        </div>
      </div>
      <div class="quote-details">
        <div class="info-row">
          <span class="info-label">Fecha:</span>
          <span><strong>${currentDate}</strong></span>
        </div>
        <div class="info-row">
          <span class="info-label">Vencimiento:</span>
          <span><strong>${validUntil || 'N/A'}</strong></span>
        </div>
      </div>
    </div>
    
    <div class="conditions-section">
      <div class="condition-box">CONDICIONES DE PAGO</div>
      <div class="condition-content">50% seña, 50% contra entrega</div>
      <div class="condition-box">PLAZO ENTREGA</div>
      <div class="condition-content">45 días</div>
    </div>
    
    <div class="conditions-section">
      <div class="condition-box">OBSERVACIONES</div>
      <div class="condition-content">El presente presupuesto incluye flete y colocación</div>
    </div>
    
    <table class="products-table">
      <thead>
        <tr>
          <th style="width: 60px;">CANT.</th>
          <th style="width: 350px;">PRODUCTO / DESCRIPCIÓN</th>
          <th style="width: 120px;">PRECIO UNITARIO</th>
          <th style="width: 120px;">IMPORTE</th>
        </tr>
      </thead>
      <tbody>
        ${items.map((item: any) => `
          <tr>
            <td class="text-center"><strong>${item.quantity}</strong></td>
            <td class="product-description">
              <div class="product-name">${item.product_name || 'Servicio'}</div>
              <div>${item.description || ''}</div>
            </td>
            <td class="text-right">USD ${parseFloat(item.unit_price).toLocaleString('es-AR', { minimumFractionDigits: 2 })}</td>
            <td class="text-right"><strong>USD ${parseFloat(item.total).toLocaleString('es-AR', { minimumFractionDigits: 2 })}</strong></td>
          </tr>
        `).join('')}
      </tbody>
    </table>
    
    <div class="totals-section">
      <table class="totals-table">
        <tr>
          <td class="label">Sub-Total</td>
          <td class="amount">USD ${(parseFloat(quote.total) / 1.21).toLocaleString('es-AR', { minimumFractionDigits: 2 })}</td>
        </tr>
        <tr>
          <td class="label">IVA (21.00%)</td>
          <td class="amount">USD ${(parseFloat(quote.total) - parseFloat(quote.total) / 1.21).toLocaleString('es-AR', { minimumFractionDigits: 2 })}</td>
        </tr>
        <tr class="total-row">
          <td class="label">TOTAL</td>
          <td class="amount">USD ${parseFloat(quote.total).toLocaleString('es-AR', { minimumFractionDigits: 2 })}</td>
        </tr>
      </table>
    </div>
    
    <div class="footer">
      <p><strong>AKUN ABERTURAS</strong> - Soluciones en Aberturas de Calidad</p>
      <p>Gracias por confiar en nosotros para su proyecto</p>
    </div>
  </div>
  
  <script>
    window.onload = function() {
      setTimeout(function() {
        window.print();
      }, 500);
    };
  </script>
</body>
</html>`;

      const newWindow = window.open();
      if (newWindow) {
        newWindow.document.write(htmlContent);
        newWindow.document.close();
      }
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('Error al generar el PDF');
    }
  };

  const getStatusColor = (status: string) => {
    const colors = {
      'DRAFT': 'bg-gray-100 text-gray-800',
      'SENT': 'bg-blue-100 text-blue-800',
      'EXPIRED': 'bg-yellow-100 text-yellow-800',
      'SOLD': 'bg-green-100 text-green-800',
      'REJECTED': 'bg-red-100 text-red-800',
    };
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  const getStatusText = (status: string) => {
    const texts = {
      'DRAFT': 'Borrador',
      'SENT': 'Enviado',
      'EXPIRED': 'Cerrado Vencido',
      'SOLD': 'Cerrado Vendido',
      'REJECTED': 'Desestimado',
    };
    return texts[status as keyof typeof texts] || status;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <>
      <header className="bg-white shadow-sm border-b px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Presupuestos</h2>
            <p className="text-gray-600">Gestión de presupuestos y cotizaciones</p>
          </div>
          <button
            onClick={() => window.location.hash = '/presupuestos/nuevo'}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Plus className="w-4 h-4 mr-2" />
            Nuevo Presupuesto
          </button>
        </div>
      </header>

      <main className="flex-1 overflow-y-auto p-6">
        <div className="max-w-7xl mx-auto">
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center space-x-4">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <input
                    type="text"
                    placeholder="Buscar presupuestos..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <button className="flex items-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                  <Filter className="w-4 h-4 mr-2" />
                  Filtros
                </button>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Número
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Cliente
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Estado
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Total
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Fecha
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Acciones
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {quotes.map((quote, index) => (
                    <tr 
                      key={quote.id} 
                      className="group hover:bg-gray-50 transition-all duration-200 hover:shadow-sm animate-fade-in"
                      style={{ animationDelay: `${index * 50}ms` }}
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {quote.number}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{quote.customer_name}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(quote.status)}`}>
                          {getStatusText(quote.status)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          ${parseFloat(quote.total).toLocaleString()}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-500">
                          {new Date(quote.created_at).toLocaleDateString()}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex items-center justify-end space-x-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                          <button
                            onClick={() => window.location.hash = `/presupuestos/${quote.id}`}
                            className="text-blue-600 hover:text-blue-900"
                            title="Ver detalle"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                          {quote.status !== 'EXPIRED' && (
                            <button
                              onClick={() => window.location.hash = `/presupuestos/${quote.id}/editar`}
                              className="text-green-600 hover:text-green-900"
                              title="Editar"
                            >
                              <Edit className="w-4 h-4" />
                            </button>
                          )}
                          <button
                            onClick={() => handleGeneratePDF(quote)}
                            className="text-purple-600 hover:text-purple-900"
                            title="Generar PDF"
                          >
                            <FileText className="w-4 h-4" />
                          </button>
                          {quote.status === 'DRAFT' && (
                            <>
                              <button
                                onClick={() => handleSendQuote(quote)}
                                className="text-green-600 hover:text-green-900"
                                title="Enviar"
                              >
                                <Send className="w-4 h-4" />
                              </button>
                              <button
                                onClick={() => handleMarkAsRejected(quote)}
                                className="text-red-600 hover:text-red-900"
                                title="Desestimado"
                              >
                                <X className="w-4 h-4" />
                              </button>
                            </>
                          )}
                          {quote.status === 'SENT' && (
                            <>
                              <button
                                onClick={() => handleConvertToSale(quote)}
                                className="text-blue-600 hover:text-blue-900"
                                title="Cerrado Vendido"
                              >
                                <CheckCircle className="w-4 h-4" />
                              </button>
                              <button
                                onClick={() => handleMarkAsRejected(quote)}
                                className="text-red-600 hover:text-red-900"
                                title="Desestimado"
                              >
                                <X className="w-4 h-4" />
                              </button>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {quotes.length === 0 && (
              <div className="text-center py-12">
                <FileText className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No hay presupuestos</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Comienza creando tu primer presupuesto.
                </p>
                <div className="mt-6">
                  <button
                    onClick={() => window.location.hash = '/presupuestos/nuevo'}
                    className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Nuevo Presupuesto
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </>
  );
};

export default QuoteList;