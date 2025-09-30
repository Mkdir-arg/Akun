import React, { useState, useEffect } from 'react';
import { Plus, Edit, Copy, Trash2, Eye, Search, Filter } from 'lucide-react';

interface ProductTemplate {
  id: number;
  product_class: string;
  line_name: string;
  code: string;
  version: number;
  is_active: boolean;
  created_at: string;
  attributes_count: number;
}

interface TemplateListProps {
  onEdit?: (templateId: number) => void;
  onPreview?: (templateId: number) => void;
}

export const TemplateList: React.FC<TemplateListProps> = ({ onEdit, onPreview }) => {
  const [templates, setTemplates] = useState<ProductTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    product_class: '',
    is_active: ''
  });
  const [showFilters, setShowFilters] = useState(false);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    fetchTemplates();
  }, [filters, searchTerm]);

  const fetchTemplates = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.product_class) params.append('class', filters.product_class);
      if (filters.is_active) params.append('active', filters.is_active);
      if (searchTerm) params.append('line_name', searchTerm);

      const response = await fetch(`/api/templates/?${params}`);
      if (response.ok) {
        const data = await response.json();
        setTemplates(data.results || data);
      }
    } catch (error) {
      console.error('Error fetching templates:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClone = async (templateId: number) => {
    try {
      const response = await fetch(`/api/templates/${templateId}/clone/`, {
        method: 'POST'
      });
      if (response.ok) {
        fetchTemplates();
      }
    } catch (error) {
      console.error('Error cloning template:', error);
    }
  };

  const handleDelete = async (templateId: number) => {
    if (!window.confirm('¿Estás seguro de eliminar esta plantilla?')) return;

    try {
      const response = await fetch(`/api/templates/${templateId}/`, {
        method: 'DELETE'
      });
      if (response.ok) {
        fetchTemplates();
      }
    } catch (error) {
      console.error('Error deleting template:', error);
    }
  };

  const getStatusBadge = (isActive: boolean) => {
    return (
      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
        isActive 
          ? 'bg-green-100 text-green-800' 
          : 'bg-red-100 text-red-800'
      }`}>
        {isActive ? 'Activo' : 'Inactivo'}
      </span>
    );
  };

  const getClassBadge = (productClass: string) => {
    const colors: Record<string, string> = {
      'VENTANA': 'bg-blue-100 text-blue-800',
      'PUERTA': 'bg-green-100 text-green-800',
      'ACCESORIO': 'bg-purple-100 text-purple-800'
    };
    
    return (
      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${colors[productClass] || 'bg-gray-100 text-gray-800'}`}>
        {productClass}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-gray-900 mb-1">Plantillas de Producto</h1>
          <p className="text-gray-600">Gestiona las plantillas de configuración de productos</p>
        </div>
        <div className="ml-4">
          <button
            onClick={() => onEdit?.(0)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors whitespace-nowrap"
          >
            <Plus size={16} />
            Nueva Plantilla
          </button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-lg border p-4 space-y-4">
        <div className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
            <input
              type="text"
              placeholder="Buscar por línea..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2"
          >
            <Filter size={16} />
            Filtros
          </button>
        </div>

        {showFilters && (
          <div className="grid grid-cols-3 gap-4 pt-4 border-t">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Clase</label>
              <select
                value={filters.product_class}
                onChange={(e) => setFilters({...filters, product_class: e.target.value})}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Todas</option>
                <option value="VENTANA">Ventana</option>
                <option value="PUERTA">Puerta</option>
                <option value="ACCESORIO">Accesorio</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Estado</label>
              <select
                value={filters.is_active}
                onChange={(e) => setFilters({...filters, is_active: e.target.value})}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Todos</option>
                <option value="true">Activo</option>
                <option value="false">Inactivo</option>
              </select>
            </div>
            <div className="flex items-end">
              <button
                onClick={() => {
                  setFilters({ product_class: '', is_active: '' });
                  setSearchTerm('');
                }}
                className="px-4 py-2 text-gray-600 hover:text-gray-800"
              >
                Limpiar filtros
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Plantilla
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Clase
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Versión
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Atributos
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Creado
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {templates.map((template) => (
                <tr key={template.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {template.line_name}
                      </div>
                      <div className="text-sm text-gray-500">
                        {template.code}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getClassBadge(template.product_class)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    v{template.version}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">
                      {template.attributes_count} atributos
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getStatusBadge(template.is_active)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(template.created_at).toLocaleDateString('es-AR')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex justify-end gap-2">
                      <button
                        onClick={() => onPreview?.(template.id)}
                        className="text-gray-400 hover:text-gray-600"
                        title="Vista previa"
                      >
                        <Eye size={16} />
                      </button>
                      <button
                        onClick={() => onEdit?.(template.id)}
                        className="text-blue-600 hover:text-blue-800"
                        title="Editar"
                      >
                        <Edit size={16} />
                      </button>
                      <button
                        onClick={() => handleClone(template.id)}
                        className="text-green-600 hover:text-green-800"
                        title="Clonar"
                      >
                        <Copy size={16} />
                      </button>
                      <button
                        onClick={() => handleDelete(template.id)}
                        className="text-red-600 hover:text-red-800"
                        title="Eliminar"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {templates.length === 0 && (
          <div className="text-center py-12">
            <div className="text-gray-500 mb-4">
              <Plus size={48} className="mx-auto mb-4 text-gray-300" />
              <p className="text-lg font-medium">No hay plantillas</p>
              <p className="text-sm">Crea tu primera plantilla para comenzar</p>
            </div>
            <button
              onClick={() => onEdit?.(0)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg"
            >
              Crear plantilla
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default TemplateList;