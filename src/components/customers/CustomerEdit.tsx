import React, { useState, useEffect } from 'react';
import { ArrowLeft, Save } from 'lucide-react';

interface CustomerEditProps {
  customerId: string;
  onBack: () => void;
  onSave: () => void;
}

const CustomerEdit: React.FC<CustomerEditProps> = ({ customerId, onBack, onSave }) => {
  const [formData, setFormData] = useState({
    type: 'EMPRESA',
    name: '',
    tax_id: '',
    email: '',
    phone: '',
    provincia: '',
    localidad: '',
    municipio: '',
    calle: '',
    numero: '',
    codigo_postal: '',
    etiqueta: '',
    status: 'ACTIVO',
    notes: ''
  });
  const [etiquetas, setEtiquetas] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCustomer();
    fetchEtiquetas();
  }, [customerId]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchEtiquetas = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/customer-tags/`, {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setEtiquetas(data.results || data);
      }
    } catch (error) {
      console.error('Error fetching etiquetas:', error);
    }
  };

  const fetchCustomer = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/customers/${customerId}/`, {
        credentials: 'include'
      });
      if (response.ok) {
        const customer = await response.json();
        setFormData({
          type: customer.type,
          name: customer.name,
          tax_id: customer.tax_id || '',
          email: customer.email || '',
          phone: customer.phone || '',
          provincia: customer.provincia || '',
          localidad: customer.localidad || '',
          municipio: customer.municipio || '',
          calle: customer.calle || '',
          numero: customer.numero || '',
          codigo_postal: customer.codigo_postal || '',
          etiqueta: customer.etiqueta || '',
          status: customer.status,
          notes: customer.notes || ''
        });
      }
    } catch (error) {
      console.error('Error fetching customer:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/customers/${customerId}/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        onSave();
      }
    } catch (error) {
      console.error('Error updating customer:', error);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
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
            <h2 className="text-2xl font-bold text-gray-900">Editar Cliente</h2>
            <p className="text-gray-600">Modificar información del cliente</p>
          </div>
        </div>
      </header>

      <main className="flex-1 overflow-y-auto p-6">
        <div className="max-w-2xl mx-auto">
          <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tipo *
                </label>
                <select
                  name="type"
                  value={formData.type}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="EMPRESA">Empresa</option>
                  <option value="PERSONA">Persona</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Estado
                </label>
                <select
                  name="status"
                  value={formData.status}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="ACTIVO">Activo</option>
                  <option value="INACTIVO">Inactivo</option>
                  <option value="POTENCIAL">Potencial</option>
                </select>
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nombre / Razón Social *
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  CUIT/DNI
                </label>
                <input
                  type="text"
                  name="tax_id"
                  value={formData.tax_id}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Teléfono
                </label>
                <input
                  type="text"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Etiqueta
                </label>
                <select
                  name="etiqueta"
                  value={formData.etiqueta}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Sin etiqueta</option>
                  {etiquetas.map((etiqueta) => (
                    <option key={etiqueta.id} value={etiqueta.id}>
                      {etiqueta.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Provincia
                </label>
                <input
                  type="text"
                  name="provincia"
                  value={formData.provincia}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Localidad
                </label>
                <input
                  type="text"
                  name="localidad"
                  value={formData.localidad}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Municipio
                </label>
                <input
                  type="text"
                  name="municipio"
                  value={formData.municipio}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Calle
                </label>
                <input
                  type="text"
                  name="calle"
                  value={formData.calle}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Número
                </label>
                <input
                  type="text"
                  name="numero"
                  value={formData.numero}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Código Postal
                </label>
                <input
                  type="text"
                  name="codigo_postal"
                  value={formData.codigo_postal}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
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

export default CustomerEdit;