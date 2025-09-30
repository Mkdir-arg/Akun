import React, { useState, useEffect } from 'react';
import { Plus, Edit, Copy, Trash2, Eye } from 'lucide-react';

interface ProductTemplate {
  id: number;
  product_class: string;
  line_name: string;
  code: string;
  version: number;
  is_active: boolean;
  created_at: string;
}

interface TemplateListProps {
  onEdit?: (templateId: number) => void;
  onPreview?: (templateId: number) => void;
}

export const TemplateList: React.FC<TemplateListProps> = ({ onEdit, onPreview }) => {
  const [templates, setTemplates] = useState<ProductTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    product_class: '',
    line_name: '',
    active: ''
  });

  useEffect(() => {
    fetchTemplates();
  }, [filters]);

  const fetchTemplates = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.product_class) params.append('class', filters.product_class);
      if (filters.line_name) params.append('line_name', filters.line_name);
      if (filters.active) params.append('active', filters.active);

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
        fetchTemplates(); // Refresh list
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
        fetchTemplates(); // Refresh list
      }
    } catch (error) {
      console.error('Error deleting template:', error);
    }
  };

  const toggleActive = async (template: ProductTemplate) => {
    try {
      const response = await fetch(`/api/templates/${template.id}/`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_active: !template.is_active })
      });
      if (response.ok) {
        fetchTemplates(); // Refresh list
      }
    } catch (error) {
      console.error('Error updating template:', error);
    }
  };

  if (loading) {
    return <div className="p-6 text-center">Cargando plantillas...</div>;
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-6 border-b">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Plantillas de Producto</h2>
            <button
              onClick={() => onEdit?.(0)} // 0 = new template
              className="bg-blue-600 text-white px-4 py-2 rounded flex items-center gap-2"
            >
              <Plus size={16} />
              Nueva Plantilla
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="p-6 border-b bg-gray-50">
          <div className="grid grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Clase</label>
              <select
                value={filters.product_class}
                onChange={(e) => setFilters({...filters, product_class: e.target.value})}
                className="w-full border rounded px-3 py-2"
              >
                <option value="">Todas</option>
                <option value="VENTANA">Ventana</option>
                <option value="PUERTA">Puerta</option>
                <option value="ACCESORIO">Accesorio</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Línea</label>
              <input
                type="text"
                value={filters.line_name}
                onChange={(e) => setFilters({...filters, line_name: e.target.value})}
                className="w-full border rounded px-3 py-2"
                placeholder="Buscar línea..."
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Estado</label>
              <select
                value={filters.active}
                onChange={(e) => setFilters({...filters, active: e.target.value})}
                className="w-full border rounded px-3 py-2"
              >
                <option value="">Todos</option>
                <option value="true">Activo</option>
                <option value="false">Inactivo</option>
              </select>
            </div>
            <div className="flex items-end">
              <button
                onClick={() => setFilters({ product_class: '', line_name: '', active: '' })}
                className="bg-gray-300 text-gray-700 px-4 py-2 rounded"
              >
                Limpiar
              </button>
            </div>
          </div>
        </div>

        {/* Templates Table */}
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Clase
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Línea
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Código
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Versión
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Estado
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Creado
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {templates.map((template) => (
                <tr key={template.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                      {template.product_class}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap font-medium">
                    {template.line_name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-gray-600">
                    {template.code}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    v{template.version}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <button
                      onClick={() => toggleActive(template)}
                      className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        template.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {template.is_active ? 'Activo' : 'Inactivo'}
                    </button>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-gray-600">
                    {new Date(template.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex gap-2">
                      <button
                        onClick={() => onPreview?.(template.id)}
                        className="text-gray-600 hover:text-gray-800"
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
          <div className="p-12 text-center text-gray-500">
            <p>No se encontraron plantillas</p>
            <button
              onClick={() => onEdit?.(0)}
              className="mt-4 bg-blue-600 text-white px-4 py-2 rounded"
            >
              Crear primera plantilla
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default TemplateList;