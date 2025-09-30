import React, { useState, useEffect } from 'react';
import { ArrowLeft, Edit, Phone, Mail, MapPin, User, FileText, Paperclip, ShoppingCart } from 'lucide-react';
import GoogleMap from '../common/GoogleMap';

interface Customer {
  id: number;
  code: string;
  name: string;
  type: string;
  tax_id: string;
  email: string;
  phone: string;
  status: string;
  credit_limit: string;
  addresses: any[];
  contacts: any[];
  customer_notes: any[];
  files: any[];
  tags: any[];
  provincia?: string;
  municipio?: string;
  localidad?: string;
  calle?: string;
  numero?: string;
  codigo_postal?: string;
  latitud?: number;
  longitud?: number;
}

interface CustomerDetailProps {
  customerId: string;
  onBack: () => void;
  onEdit: () => void;
}

const CustomerDetail: React.FC<CustomerDetailProps> = ({ customerId, onBack, onEdit }) => {
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCustomer();
  }, [customerId]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchCustomer = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/customers/${customerId}/`, {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setCustomer(data);
      }
    } catch (error) {
      console.error('Error fetching customer:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!customer) {
    return <div>Cliente no encontrado</div>;
  }

  const getStatusBadge = (status: string) => {
    const badges = {
      'ACTIVO': 'bg-green-100 text-green-800',
      'INACTIVO': 'bg-gray-100 text-gray-800',
      'POTENCIAL': 'bg-blue-100 text-blue-800'
    };
    return badges[status as keyof typeof badges] || 'bg-gray-100 text-gray-800';
  };

  const tabs = [
    { id: 'overview', label: 'Resumen', icon: User },
    { id: 'addresses', label: 'Direcciones', icon: MapPin },
    { id: 'contacts', label: 'Contactos', icon: Phone },
    { id: 'notes', label: 'Notas', icon: FileText },
    { id: 'files', label: 'Archivos', icon: Paperclip },
  ];

  return (
    <>
      <header className="bg-white shadow-sm border-b px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <button onClick={onBack} className="mr-4 p-2 hover:bg-gray-100 rounded-lg">
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">{customer.name}</h2>
              <p className="text-gray-600">{customer.code}</p>
            </div>
          </div>
          <button
            onClick={onEdit}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            <Edit className="w-4 h-4 mr-2" />
            Editar
          </button>
        </div>
      </header>

      <main className="flex-1 overflow-y-auto">
        <div className="bg-white border-b px-6 py-4">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
              <span className="text-xl font-bold text-blue-700">
                {customer.name.charAt(0).toUpperCase()}
              </span>
            </div>
            <div className="flex-1">
              <div className="flex items-center space-x-3 mb-2">
                <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusBadge(customer.status)}`}>
                  {customer.status}
                </span>
                <span className="px-2 py-1 text-xs font-semibold rounded-full bg-purple-100 text-purple-800">
                  {customer.type}
                </span>
                {customer.tags && customer.tags.map((tag: any) => (
                  <span
                    key={tag.id}
                    className="px-2 py-1 text-xs font-semibold rounded-full text-white"
                    style={{ backgroundColor: tag.color }}
                  >
                    {tag.name}
                  </span>
                ))}
              </div>
              <div className="flex items-center space-x-4 text-sm text-gray-600">
                {customer.email && (
                  <div className="flex items-center">
                    <Mail className="w-4 h-4 mr-1" />
                    {customer.email}
                  </div>
                )}
                {customer.phone && (
                  <div className="flex items-center">
                    <Phone className="w-4 h-4 mr-1" />
                    {customer.phone}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white border-b">
          <nav className="flex space-x-8 px-6">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  <Icon className="w-4 h-4 mr-2" />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-medium mb-4">Información General</h3>
                  <dl className="space-y-3">
                    <div>
                      <dt className="text-sm font-medium text-gray-500">CUIT/DNI</dt>
                      <dd className="text-sm text-gray-900">{customer.tax_id || '-'}</dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Límite de Crédito</dt>
                      <dd className="text-sm text-gray-900">${parseFloat(customer.credit_limit).toLocaleString()}</dd>
                    </div>
                  </dl>
                </div>
                
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-medium mb-4">Contacto Principal</h3>
                  {customer.contacts.find(c => c.is_primary) ? (
                    <div>
                      {(() => {
                        const primary = customer.contacts.find(c => c.is_primary);
                        return (
                          <div>
                            <p className="font-medium">{primary.full_name}</p>
                            <p className="text-sm text-gray-600">{primary.role}</p>
                            <p className="text-sm text-gray-600">{primary.email}</p>
                            <p className="text-sm text-gray-600">{primary.phone}</p>
                          </div>
                        );
                      })()}
                    </div>
                  ) : (
                    <p className="text-gray-500">No hay contacto principal</p>
                  )}
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow">
                <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                  <h3 className="text-lg font-medium">Pedidos del Cliente</h3>
                  <button className="flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700">
                    <ShoppingCart className="w-4 h-4 mr-2" />
                    Crear Pedido
                  </button>
                </div>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Número</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      <tr>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900">PED-001</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">15/09/2024</td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800">
                            Pendiente
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">$45.000</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <button className="text-blue-600 hover:text-blue-900">Ver</button>
                        </td>
                      </tr>
                      <tr>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900">PED-002</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">10/09/2024</td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                            Completado
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">$78.500</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <button className="text-blue-600 hover:text-blue-900">Ver</button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'addresses' && (
            <div className="space-y-6">
              {/* Información de Domicilio */}
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-medium mb-4">Información de Domicilio</h3>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="space-y-3">
                    {customer.provincia && (
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Provincia</dt>
                        <dd className="text-sm text-gray-900">{customer.provincia}</dd>
                      </div>
                    )}
                    {customer.municipio && (
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Municipio</dt>
                        <dd className="text-sm text-gray-900">{customer.municipio}</dd>
                      </div>
                    )}
                    {customer.localidad && (
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Localidad</dt>
                        <dd className="text-sm text-gray-900">{customer.localidad}</dd>
                      </div>
                    )}
                    {customer.calle && (
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Calle</dt>
                        <dd className="text-sm text-gray-900">{customer.calle} {customer.numero}</dd>
                      </div>
                    )}
                    {customer.codigo_postal && (
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Código Postal</dt>
                        <dd className="text-sm text-gray-900">{customer.codigo_postal}</dd>
                      </div>
                    )}
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500 mb-3">Ubicación en el Mapa</dt>
                    <GoogleMap
                      calle={customer.calle}
                      numero={customer.numero}
                      localidad={customer.localidad}
                      municipio={customer.municipio}
                      provincia={customer.provincia}
                      latitud={customer.latitud}
                      longitud={customer.longitud}
                      height="250px"
                    />
                  </div>
                </div>
              </div>
              
              {/* Direcciones Adicionales */}
              {customer.addresses && customer.addresses.length > 0 && (
                <div>
                  <h3 className="text-lg font-medium mb-4">Direcciones Adicionales</h3>
                  <div className="space-y-4">
                    {customer.addresses.map((address: any) => (
                      <div key={address.id} className="bg-white rounded-lg shadow p-6">
                        <div className="flex justify-between items-start">
                          <div>
                            <div className="flex items-center mb-2">
                              <h4 className="font-medium">{address.kind}</h4>
                              {address.is_default && (
                                <span className="ml-2 px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">
                                  Por defecto
                                </span>
                              )}
                            </div>
                            <p className="text-gray-600">
                              {address.street} {address.number}
                            </p>
                            <p className="text-gray-600">
                              {address.city}, {address.province} ({address.postal_code})
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'contacts' && (
            <div className="space-y-4">
              {customer.contacts.map((contact: any) => (
                <div key={contact.id} className="bg-white rounded-lg shadow p-6">
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="flex items-center mb-2">
                        <h4 className="font-medium">{contact.full_name}</h4>
                        {contact.is_primary && (
                          <span className="ml-2 px-2 py-1 text-xs bg-green-100 text-green-800 rounded">
                            Principal
                          </span>
                        )}
                      </div>
                      <p className="text-gray-600">{contact.role}</p>
                      <p className="text-gray-600">{contact.email}</p>
                      <p className="text-gray-600">{contact.phone}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'notes' && (
            <div className="space-y-4">
              {customer.customer_notes.map((note: any) => (
                <div key={note.id} className="bg-white rounded-lg shadow p-6">
                  <div className="flex justify-between items-start mb-3">
                    <div className="flex items-center">
                      <span className="font-medium">{note.author_name}</span>
                      {note.pinned && (
                        <span className="ml-2 px-2 py-1 text-xs bg-yellow-100 text-yellow-800 rounded">
                          Fijada
                        </span>
                      )}
                    </div>
                    <span className="text-sm text-gray-500">
                      {new Date(note.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <p className="text-gray-700">{note.body}</p>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'files' && (
            <div className="space-y-4">
              {customer.files.map((file: any) => (
                <div key={file.id} className="bg-white rounded-lg shadow p-6">
                  <div className="flex justify-between items-center">
                    <div>
                      <h4 className="font-medium">{file.title || file.file}</h4>
                      <p className="text-sm text-gray-600">
                        Subido por {file.uploaded_by_name} el {new Date(file.uploaded_at).toLocaleDateString()}
                      </p>
                    </div>
                    <button className="text-blue-600 hover:text-blue-800">
                      Descargar
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </>
  );
};

export default CustomerDetail;