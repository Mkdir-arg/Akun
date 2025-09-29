import React, { useState, useEffect } from 'react';
import { Search, Plus, Filter, Download, Upload } from 'lucide-react';

interface Customer {
  id: number;
  code: string;
  name: string;
  type: 'PERSONA' | 'EMPRESA';
  tax_id: string;
  email: string;
  phone: string;
  status: 'ACTIVO' | 'INACTIVO' | 'POTENCIAL';
  direccion_completa: string;
  created_at: string;
  updated_at: string;
  etiqueta_name?: string;
}

const CustomerList: React.FC = () => {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  const [direccionFilter, setDireccionFilter] = useState('');

  useEffect(() => {
    fetchCustomers();
  }, [searchTerm, statusFilter, direccionFilter]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchCustomers = async () => {
    try {
      const params = new URLSearchParams();
      if (searchTerm) params.append('search', searchTerm);
      if (statusFilter) params.append('status', statusFilter);

      if (direccionFilter) params.append('direccion', direccionFilter);

      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/customers/?${params}`, {
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

  const getStatusBadge = (status: string) => {
    const badges = {
      'ACTIVO': 'bg-green-100 text-green-800',
      'INACTIVO': 'bg-gray-100 text-gray-800',
      'POTENCIAL': 'bg-blue-100 text-blue-800'
    };
    return badges[status as keyof typeof badges] || 'bg-gray-100 text-gray-800';
  };



  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <>
      {/* Top Header */}
      <header className="bg-white shadow-sm border-b px-6 py-4">
        <h2 className="text-2xl font-bold text-gray-900">Clientes</h2>
        <p className="text-gray-600">Gestión de clientes y contactos</p>
      </header>
      
      {/* Content Area */}
      <main className="flex-1 overflow-y-auto p-6">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
        <div className="flex gap-2">
          <button className="flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
            <Upload className="w-4 h-4 mr-2" />
            Importar
          </button>
          <button className="flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
            <Download className="w-4 h-4 mr-2" />
            Exportar
          </button>
          <button 
            onClick={() => window.location.hash = '/clientes/nuevo'}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700"
          >
            <Plus className="w-4 h-4 mr-2" />
            Nuevo Cliente
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
        <div className="p-4">
          <div className="flex flex-wrap gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Buscar clientes..."
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            
            <select
              className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="">Todos los estados</option>
              <option value="ACTIVO">Activo</option>
              <option value="INACTIVO">Inactivo</option>
              <option value="POTENCIAL">Potencial</option>
            </select>

            <input
              type="text"
              placeholder="Filtrar por dirección..."
              className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={direccionFilter}
              onChange={(e) => setDireccionFilter(e.target.value)}
            />

            <button className="flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
              <Filter className="w-4 h-4 mr-2" />
              Más filtros
            </button>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Código</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nombre</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Dirección</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {customers.map((customer) => (
                <tr key={customer.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900">{customer.code}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{customer.name}</div>
                    {customer.etiqueta_name && (
                      <div className="text-xs text-blue-600">{customer.etiqueta_name}</div>
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate">
                    {customer.direccion_completa || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{customer.email || '-'}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusBadge(customer.status)}`}>
                      {customer.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex gap-2">
                      <button 
                        onClick={() => {
                          if (window.confirm('¿Estás seguro de que quieres editar este cliente?')) {
                            window.location.hash = `/clientes/${customer.id}/editar`;
                          }
                        }}
                        className="text-indigo-600 hover:text-indigo-900"
                      >
                        Editar
                      </button>
                      <button 
                        onClick={() => window.location.hash = `/clientes/${customer.id}`}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        Ver
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

        {customers.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">No se encontraron clientes</p>
          </div>
        )}
      </main>
    </>
  );
};

export default CustomerList;