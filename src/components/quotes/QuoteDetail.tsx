import React, { useState, useEffect } from 'react';
import { ArrowLeft, Plus, Trash2 } from 'lucide-react';
import PDFGenerator from './PDFGenerator';

interface QuoteDetailProps {
  quoteId: string;
  onBack: () => void;
}

interface Quote {
  id: number;
  number: string;
  customer_name: string;
  status: string;
  priority: string;
  valid_until: string;
  subtotal: string;
  tax_amount: string;
  total: string;
  notes: string;
  created_at: string;
}

interface QuoteItem {
  id: number;
  product: number;
  product_name: string;
  product_sku: string;
  description: string;
  quantity: string;
  unit_price: string;
  discount_pct: string;
  tax_rate: string;
  total: string;
  line_number: number;
  assigned_to: number;
  assigned_to_name: string;
  currency: number;
  currency_code: string;
}

interface Product {
  id: number;
  name: string;
  sku: string;
  pricing_method: string;
  base_price: string;
  price_per_m2: string;
  currency: number;
  currency_code: string;
}

interface Currency {
  id: number;
  code: string;
  name: string;
  symbol: string;
}

const QuoteDetail: React.FC<QuoteDetailProps> = ({ quoteId, onBack }) => {
  const [quote, setQuote] = useState<Quote | null>(null);
  const [items, setItems] = useState<QuoteItem[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [currencies, setCurrencies] = useState<Currency[]>([]);
  const [showAddProduct, setShowAddProduct] = useState(false);
  const [loading, setLoading] = useState(true);

  const [newItem, setNewItem] = useState({
    type: 'PRODUCTO', // PRODUCTO o SERVICIO
    product: '',
    service_type: '',
    assigned_to: '',
    quantity: '1',
    days: '1',
    unit_price: '0',
    discount_pct: '0',
    tax_rate: '21.00',
    description: '',
    currency: '1'
  });

  const [users, setUsers] = useState<any[]>([]);

  useEffect(() => {
    const loadData = async () => {
      await fetchQuote();
      await fetchItems();
      await fetchProducts();
      await fetchUsers();
      await fetchCurrencies();
    };
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [quoteId]);

  const fetchQuote = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/quotes/${quoteId}/`, {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setQuote(data);
      }
    } catch (error) {
      console.error('Error fetching quote:', error);
    }
  };

  const fetchItems = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/quote-items/?quote=${quoteId}`, {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setItems(data.results || data);
      }
    } catch (error) {
      console.error('Error fetching items:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchProducts = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/products/`, {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setProducts(data.results || data);
      }
    } catch (error) {
      console.error('Error fetching products:', error);
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/users/?role_name=Colocadores`, {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setUsers(data.results || data);
      }
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const fetchCurrencies = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/currencies/`, {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setCurrencies(data.results || data);
      }
    } catch (error) {
      console.error('Error fetching currencies:', error);
    }
  };

  const handleProductSelect = (productId: string) => {
    const product = products.find(p => p.id.toString() === productId);
    if (product) {
      const price = product.pricing_method === 'FIXED' ? product.base_price : product.price_per_m2;
      setNewItem({
        ...newItem,
        product: productId,
        unit_price: price,
        tax_rate: product.tax_rate || '21.00',
        description: product.name,
        currency: product.currency.toString()
      });
    }
  };

  const handleAddItem = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const quantity = newItem.type === 'SERVICIO' ? parseFloat(newItem.days) : parseFloat(newItem.quantity);
    
    const itemData = {
      quote: parseInt(quoteId),
      product: newItem.type === 'PRODUCTO' ? parseInt(newItem.product) : null,
      quantity: quantity,
      unit_price: parseFloat(newItem.unit_price),
      discount_pct: parseFloat(newItem.discount_pct),
      tax_rate: parseFloat(newItem.tax_rate),
      currency: parseInt(newItem.currency),
      description: newItem.type === 'SERVICIO' ? 
        `${newItem.service_type} - ${newItem.description}` : 
        newItem.description || '',
      line_number: items.length + 1,
      assigned_to: newItem.type === 'SERVICIO' && newItem.assigned_to ? parseInt(newItem.assigned_to) : null
    };
    
    console.log('Sending item data:', itemData);
    console.log('Quote ID:', quoteId);
    
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/quote-items/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(itemData)
      });

      if (response.ok) {
        setShowAddProduct(false);
        setNewItem({
          type: 'PRODUCTO',
          product: '',
          service_type: '',
          assigned_to: '',
          quantity: '1',
          days: '1',
          unit_price: '0',
          discount_pct: '0',
          tax_rate: '21.00',
          description: '',
          currency: '1'
        });
        fetchItems();
        fetchQuote();
      }
    } catch (error) {
      console.error('Error adding item:', error);
    }
  };

  const handleDeleteItem = async (itemId: number) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/quote-items/${itemId}/`, {
        method: 'DELETE',
        credentials: 'include'
      });

      if (response.ok) {
        fetchItems();
        fetchQuote();
      }
    } catch (error) {
      console.error('Error deleting item:', error);
    }
  };

  const handleSendQuote = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/quotes/${quoteId}/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ status: 'SENT' })
      });

      if (response.ok) {
        fetchQuote();
        alert('Presupuesto enviado exitosamente');
      }
    } catch (error) {
      console.error('Error sending quote:', error);
    }
  };

  const handleMarkAsSold = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/quotes/${quoteId}/convert_to_order/`, {
        method: 'POST',
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        fetchQuote();
        alert(`Presupuesto convertido a venta. Pedido ${data.order_number} creado.`);
      }
    } catch (error) {
      console.error('Error converting to sale:', error);
    }
  };

  const handleMarkAsRejected = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/quotes/${quoteId}/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ status: 'REJECTED' })
      });

      if (response.ok) {
        fetchQuote();
        alert('Presupuesto marcado como desestimado');
      }
    } catch (error) {
      console.error('Error marking as rejected:', error);
    }
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

  const getPriorityText = (priority: string) => {
    const texts = {
      'LOW': 'Baja',
      'MEDIUM': 'Media',
      'HIGH': 'Alta',
      'URGENT': 'Urgente',
    };
    return texts[priority as keyof typeof texts] || priority;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!quote) {
    return <div>Presupuesto no encontrado</div>;
  }

  return (
    <>
      <header className="bg-white shadow-sm border-b px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <button onClick={onBack} className="mr-4 p-2 hover:bg-gray-100 rounded-lg">
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">{quote.number}</h2>
              <p className="text-gray-600">{quote.customer_name}</p>
            </div>
          </div>
          <div className="flex gap-3">
            <PDFGenerator quote={quote} items={items} />
            {quote.status === 'DRAFT' && (
              <>
                <button
                  onClick={() => handleSendQuote()}
                  className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                >
                  Enviar
                </button>
                <button
                  onClick={() => handleMarkAsRejected()}
                  className="flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                >
                  Desestimado
                </button>
              </>
            )}
            {quote.status === 'SENT' && (
              <>
                <button
                  onClick={() => handleMarkAsSold()}
                  className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Cerrado Vendido
                </button>
                <button
                  onClick={() => handleMarkAsRejected()}
                  className="flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                >
                  Desestimado
                </button>
              </>
            )}
            {quote.status === 'DRAFT' && (
              <button
                onClick={() => setShowAddProduct(true)}
                className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                <Plus className="w-4 h-4 mr-2" />
                Agregar Producto
              </button>
            )}
          </div>
        </div>
      </header>

      <main className="flex-1 overflow-y-auto p-6">
        <div className="max-w-6xl mx-auto space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Información General</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-gray-500">Estado:</span>
                <p className="font-medium">{getStatusText(quote.status)}</p>
              </div>
              <div>
                <span className="text-gray-500">Prioridad:</span>
                <p className="font-medium">{getPriorityText(quote.priority)}</p>
              </div>
              <div>
                <span className="text-gray-500">Válido hasta:</span>
                <p className="font-medium">{quote.valid_until || 'N/A'}</p>
              </div>
              <div>
                <span className="text-gray-500">Total:</span>
                <p className="font-medium text-lg">${parseFloat(quote.total).toLocaleString()}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b">
              <h3 className="text-lg font-semibold">Productos y Servicios</h3>
            </div>
            
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Producto</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cantidad</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Precio Unit.</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">IVA (%)</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Moneda</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Descuento</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Acciones</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {items.map((item) => (
                    <tr key={item.id}>
                      <td className="px-6 py-4">
                        <div>
                          {item.product_name ? (
                            <>
                              <div className="text-sm font-medium text-gray-900">{item.product_name}</div>
                              <div className="text-sm text-gray-500">{item.product_sku}</div>
                              {item.description && (
                                <div className="text-sm text-gray-500 mt-1">{item.description}</div>
                              )}
                            </>
                          ) : (
                            <>
                              <div className="text-sm font-medium text-gray-900">
                                {item.description.split(' - ')[0] || 'Servicio'}
                              </div>
                              <div className="text-sm text-gray-500">SERV-{String(item.id).padStart(3, '0')}</div>
                              <div className="text-sm text-gray-500 mt-1">
                                {item.description.split(' - ')[1] || item.description}
                              </div>
                              {item.assigned_to_name && (
                                <div className="text-sm text-blue-600 mt-1">
                                  Asignado a: {item.assigned_to_name}
                                </div>
                              )}
                            </>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">{item.quantity}</td>
                      <td className="px-6 py-4 text-sm text-gray-900">${parseFloat(item.unit_price).toLocaleString()}</td>
                      <td className="px-6 py-4 text-sm text-gray-900">{item.tax_rate}%</td>
                      <td className="px-6 py-4 text-sm text-gray-900">{item.currency_code || 'USD'}</td>
                      <td className="px-6 py-4 text-sm text-gray-900">{item.discount_pct}%</td>
                      <td className="px-6 py-4 text-sm font-medium text-gray-900">${parseFloat(item.total).toLocaleString()}</td>
                      <td className="px-6 py-4 text-right">
                        {quote.status === 'DRAFT' && (
                          <button
                            onClick={() => handleDeleteItem(item.id)}
                            className="text-red-600 hover:text-red-900"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {items.length === 0 && (
              <div className="text-center py-12">
                <p className="text-gray-500">No hay productos agregados</p>
                <button
                  onClick={() => setShowAddProduct(true)}
                  className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Agregar Primer Producto
                </button>
              </div>
            )}

            {items.length > 0 && (
              <div className="bg-gray-50 px-6 py-4">
                <div className="flex justify-end">
                  <div className="w-64 space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Subtotal:</span>
                      <span>${parseFloat(quote.subtotal).toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>IVA:</span>
                      <span>${parseFloat(quote.tax_amount).toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between text-lg font-semibold border-t pt-2">
                      <span>Total:</span>
                      <span>${parseFloat(quote.total).toLocaleString()}</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      {showAddProduct && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-semibold mb-4">Agregar Producto</h3>
            <form onSubmit={handleAddItem} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Tipo</label>
                <select
                  value={newItem.type}
                  onChange={(e) => setNewItem({...newItem, type: e.target.value, product: '', service_type: '', assigned_to: '', tax_rate: '21.00'})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="PRODUCTO">Producto</option>
                  <option value="SERVICIO">Servicio</option>
                </select>
              </div>

              {newItem.type === 'PRODUCTO' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Producto</label>
                  <select
                    value={newItem.product}
                    onChange={(e) => handleProductSelect(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  >
                    <option value="">Seleccionar producto</option>
                    {products.map((product) => (
                      <option key={product.id} value={product.id}>
                        {product.name} - {product.sku}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {newItem.type === 'SERVICIO' && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Tipo de Servicio</label>
                    <select
                      value={newItem.service_type}
                      onChange={(e) => setNewItem({...newItem, service_type: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    >
                      <option value="">Seleccionar tipo de servicio</option>
                      <option value="INSTALACION">Instalación</option>
                      <option value="COLOCACION">Colocación</option>
                      <option value="MANTENIMIENTO">Mantenimiento</option>
                      <option value="REPARACION">Reparación</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Encargado</label>
                    <select
                      value={newItem.assigned_to}
                      onChange={(e) => setNewItem({...newItem, assigned_to: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    >
                      <option value="">Seleccionar encargado</option>
                      {users.map((user) => (
                        <option key={user.id} value={user.id}>
                          {user.first_name} {user.last_name} - {user.email}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Días</label>
                    <input
                      type="number"
                      value={newItem.days}
                      onChange={(e) => setNewItem({...newItem, days: e.target.value})}
                      min="1"
                      step="1"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>
                </>
              )}

              <div className={`grid gap-4 ${newItem.type === 'PRODUCTO' ? 'grid-cols-2' : 'grid-cols-1'}`}>
                {newItem.type === 'PRODUCTO' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Cantidad</label>
                    <input
                      type="number"
                      value={newItem.quantity}
                      onChange={(e) => setNewItem({...newItem, quantity: e.target.value})}
                      min="0.01"
                      step="0.01"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>
                )}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">{newItem.type === 'PRODUCTO' ? 'Precio Unitario' : 'Precio del Servicio'}</label>
                  <input
                    type="number"
                    value={newItem.unit_price}
                    onChange={(e) => setNewItem({...newItem, unit_price: e.target.value})}
                    min="0"
                    step="0.01"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Moneda</label>
                <select
                  value={newItem.currency}
                  onChange={(e) => setNewItem({...newItem, currency: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                >
                  {currencies.map((currency) => (
                    <option key={currency.id} value={currency.id}>
                      {currency.name} ({currency.code})
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Descuento (%)</label>
                  <input
                    type="number"
                    value={newItem.discount_pct}
                    onChange={(e) => setNewItem({...newItem, discount_pct: e.target.value})}
                    min="0"
                    max="100"
                    step="0.01"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">IVA (%)</label>
                  <input
                    type="number"
                    value={newItem.tax_rate}
                    onChange={(e) => setNewItem({...newItem, tax_rate: e.target.value})}
                    min="0"
                    max="100"
                    step="0.01"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
              </div>

              {newItem.type === 'SERVICIO' && (
                <div className="bg-gray-50 p-4 rounded-lg border">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Cálculo del Costo</h4>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span>Días: {newItem.days}</span>
                      <span>Precio por día: ${parseFloat(newItem.unit_price || '0').toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Subtotal:</span>
                      <span>${(parseFloat(newItem.days || '1') * parseFloat(newItem.unit_price || '0')).toLocaleString()}</span>
                    </div>
                    {parseFloat(newItem.discount_pct || '0') > 0 && (
                      <div className="flex justify-between text-red-600">
                        <span>Descuento ({newItem.discount_pct}%):</span>
                        <span>-${((parseFloat(newItem.days || '1') * parseFloat(newItem.unit_price || '0')) * (parseFloat(newItem.discount_pct || '0') / 100)).toLocaleString()}</span>
                      </div>
                    )}
                    <div className="flex justify-between font-semibold border-t pt-1">
                      <span>Total:</span>
                      <span>${((parseFloat(newItem.days || '1') * parseFloat(newItem.unit_price || '0')) * (1 - parseFloat(newItem.discount_pct || '0') / 100)).toLocaleString()}</span>
                    </div>
                  </div>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Descripción adicional</label>
                <textarea
                  value={newItem.description}
                  onChange={(e) => setNewItem({...newItem, description: e.target.value})}
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowAddProduct(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  Agregar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
};

export default QuoteDetail;