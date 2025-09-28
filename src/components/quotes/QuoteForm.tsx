import React, { useState, useEffect } from 'react';
import { ArrowLeft, Save } from 'lucide-react';

interface QuoteFormProps {
  onBack: () => void;
  onSave: () => void;
}

interface Customer {
  id: number;
  name: string;
  tax_id: string;
  email: string;
  phone: string;
  credit_limit: string;
  status: string;
}

const QuoteForm: React.FC<QuoteFormProps> = ({ onBack, onSave }) => {
  const [formData, setFormData] = useState({
    customer: '',
    priority: 'MEDIUM',
    valid_until: '',
    estimated_delivery_days: '15',
    notes: ''
  });

  const [customers, setCustomers] = useState<Customer[]>([]);
  const [filteredCustomers, setFilteredCustomers] = useState<Customer[]>([]);
  const [customerSearch, setCustomerSearch] = useState('');
  const [showCustomerDropdown, setShowCustomerDropdown] = useState(false);
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCustomers();
  }, []);

  useEffect(() => {
    if (customerSearch) {
      const filtered = customers.filter(customer => 
        customer.name.toLowerCase().includes(customerSearch.toLowerCase())
      );
      setFilteredCustomers(filtered);
    } else {
      setFilteredCustomers(customers);
    }
  }, [customerSearch, customers]);

  const fetchCustomers = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/customers/`, {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setCustomers(data.results || data);
      }
    } catch (error) {
      console.error('Error fetching customers:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/quotes/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          ...formData,
          customer: parseInt(formData.customer),
          title: `Presupuesto para ${selectedCustomer?.name || 'Cliente'}`,
          estimated_delivery_days: parseInt(formData.estimated_delivery_days)
        })
      });

      if (response.ok) {
        onSave();
      }
    } catch (error) {
      console.error('Error creating quote:', error);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleCustomerSelect = (customer: Customer) => {
    setSelectedCustomer(customer);
    setCustomerSearch(customer.name);
    setFormData({ ...formData, customer: customer.id.toString() });
    setShowCustomerDropdown(false);
  };

  const handleCustomerSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCustomerSearch(e.target.value);
    setShowCustomerDropdown(true);
    if (!e.target.value) {
      setSelectedCustomer(null);
      setFormData({ ...formData, customer: '' });
    }
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
        <div className="flex items-center">
          <button onClick={onBack} className="mr-4 p-2 hover:bg-gray-100 rounded-lg">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Nuevo Presupuesto</h2>
            <p className="text-gray-600">Crear un nuevo presupuesto</p>
          </div>
        </div>
      </header>

      <main className="flex-1 overflow-y-auto p-6">
        <div className="max-w-2xl mx-auto">
          <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-6">
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Cliente *
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={customerSearch}
                  onChange={handleCustomerSearchChange}
                  onFocus={() => {
                    setShowCustomerDropdown(true);
                    if (!customerSearch) setFilteredCustomers(customers);
                  }}
                  onBlur={() => setTimeout(() => setShowCustomerDropdown(false), 200)}
                  placeholder="Escriba para buscar cliente..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                  autoComplete="off"
                />
                {showCustomerDropdown && (
                  <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-y-auto">
                    {filteredCustomers.length > 0 ? (
                      filteredCustomers.map((customer) => (
                        <div
                          key={customer.id}
                          onClick={() => handleCustomerSelect(customer)}
                          className="px-3 py-2 hover:bg-blue-50 cursor-pointer border-b border-gray-100 last:border-b-0 text-sm"
                        >
                          {customer.name}
                        </div>
                      ))
                    ) : customerSearch ? (
                      <div className="px-3 py-2 text-gray-500 text-sm">
                        No se encontraron clientes
                      </div>
                    ) : (
                      <div className="px-3 py-2 text-gray-500 text-sm">
                        Escriba para buscar...
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>

            {selectedCustomer && (
              <div className="mb-6">
                <div className="bg-gray-50 rounded-lg p-4 border">
                  <h4 className="text-sm font-medium text-gray-700 mb-3">Información del Cliente</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
                    <div className="flex flex-col">
                      <span className="text-gray-500 text-xs mb-1">CUIT/DNI</span>
                      <span className="font-medium">{selectedCustomer.tax_id || 'N/A'}</span>
                    </div>
                    <div className="flex flex-col">
                      <span className="text-gray-500 text-xs mb-1">Email</span>
                      <span className="font-medium truncate">{selectedCustomer.email || 'N/A'}</span>
                    </div>
                    <div className="flex flex-col">
                      <span className="text-gray-500 text-xs mb-1">Teléfono</span>
                      <span className="font-medium">{selectedCustomer.phone || 'N/A'}</span>
                    </div>
                    <div className="flex flex-col">
                      <span className="text-gray-500 text-xs mb-1">Límite Crédito</span>
                      <span className="font-medium">${parseFloat(selectedCustomer.credit_limit || '0').toLocaleString()}</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">



              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Prioridad
                </label>
                <select
                  name="priority"
                  value={formData.priority}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="LOW">Baja</option>
                  <option value="MEDIUM">Media</option>
                  <option value="HIGH">Alta</option>
                  <option value="URGENT">Urgente</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Válido hasta
                </label>
                <input
                  type="date"
                  name="valid_until"
                  value={formData.valid_until}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Entrega estimada (días)
                </label>
                <select
                  name="estimated_delivery_days"
                  value={formData.estimated_delivery_days}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {Array.from({ length: 18 }, (_, i) => (i + 1) * 5).map(days => (
                    <option key={days} value={days}>
                      {days} días
                    </option>
                  ))}
                </select>
              </div>



              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Notas
                </label>
                <textarea
                  name="notes"
                  value={formData.notes}
                  onChange={handleChange}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <button
                type="button"
                onClick={onBack}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              >
                Cancelar
              </button>
              <button
                type="submit"
                className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                <Save className="w-4 h-4 mr-2" />
                Guardar
              </button>
            </div>
          </form>
        </div>
      </main>
    </>
  );
};

export default QuoteForm;