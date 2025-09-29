import React, { useState, useEffect } from 'react';
import { ArrowLeft, Save } from 'lucide-react';
import GeographicInputs from '../common/GeographicInputs';

interface CustomerFormProps {
  onBack: () => void;
  onSave: (customer: any) => void;
}

const CustomerForm: React.FC<CustomerFormProps> = ({ onBack, onSave }) => {
  const [formData, setFormData] = useState({
    type: 'EMPRESA',
    name: '',
    tax_id: '',
    email: '',
    phone: '',
    provincia: '',
    municipio: '',
    localidad: '',
    calle: '',
    numero: '',
    codigo_postal: '',
    etiqueta: '',
    status: 'ACTIVO',
    notes: ''
  });

  const [etiquetas, setEtiquetas] = useState<any[]>([]);

  useEffect(() => {
    fetchEtiquetas();
  }, []);

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/customers/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        const customer = await response.json();
        onSave(customer);
      }
    } catch (error) {
      console.error('Error creating customer:', error);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <>
      <header className="bg-white shadow-sm border-b px-6 py-4">
        <div className="flex items-center">
          <button
            onClick={onBack}
            className="mr-4 p-2 hover:bg-gray-100 rounded-lg"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Nuevo Cliente</h2>
            <p className="text-gray-600">Crear un nuevo cliente</p>
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

              <div className="md:col-span-2 grid grid-cols-1 md:grid-cols-3 gap-6">
                <GeographicInputs
                  provincia={formData.provincia}
                  municipio={formData.municipio}
                  localidad={formData.localidad}
                  onProvinciaChange={(value) => {
                  console.log('CustomerForm updating provincia to:', value);
                  setFormData(prev => ({...prev, provincia: value}));
                }}
                  onMunicipioChange={(value) => setFormData(prev => ({...prev, municipio: value}))}
                  onLocalidadChange={(value) => setFormData(prev => ({...prev, localidad: value}))}
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

export default CustomerForm;