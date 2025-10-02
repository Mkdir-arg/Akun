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
  const [groupedTemplates, setGroupedTemplates] = useState<Record<string, ProductTemplate[]>>({});
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    product_class: '',
    is_active: ''
  });
  const [showFilters, setShowFilters] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedProductClass, setSelectedProductClass] = useState<string | null>(null);
  const [selectedLine, setSelectedLine] = useState<string | null>(null);
  const [showNewTemplateForm, setShowNewTemplateForm] = useState(false);
  const [newTemplateName, setNewTemplateName] = useState('');
  const itemsPerPage = 10;

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    fetchTemplates();
    setCurrentPage(1);
    setSelectedProductClass(null);
    setSelectedLine(null);
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
        const templateList = data.templates || data.results || data || [];
        setTemplates(templateList);
        
        // Agrupar por product_class (VENTANA, PUERTA, etc)
        const grouped = templateList.reduce((acc: Record<string, ProductTemplate[]>, template: ProductTemplate) => {
          const productClass = template.product_class;
          if (!acc[productClass]) acc[productClass] = [];
          acc[productClass].push(template);
          return acc;
        }, {});
        setGroupedTemplates(grouped);
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
          <h1 className="text-2xl font-bold text-gray-900 mb-1">
            Plantillas de Plantilla
            {selectedProductClass && (
              <span className="text-lg font-medium text-blue-600 ml-2">- {selectedProductClass}</span>
            )}
          </h1>
          <p className="text-gray-600">
            {selectedProductClass 
              ? `Líneas disponibles en la categoría ${selectedProductClass}` 
              : 'Gestiona las plantillas de configuración de productos'
            }
          </p>
        </div>
        <div className="ml-4">
          <button
            onClick={() => setShowNewTemplateForm(true)}
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
        <div className="overflow-x-auto max-h-[600px] overflow-y-auto">
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
              {selectedLine ? (
                // Nivel 3: Productos específicos de la línea seleccionada
                (() => {
                  const lineTemplates = templates.filter(t => t.product_class === selectedProductClass && t.line_name === selectedLine);
                  return lineTemplates.map((template) => (
                    <tr key={template.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {template.code}
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
                          {template.attributes_count || 5} atributos
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
                        </div>
                      </td>
                    </tr>
                  ));
                })()
              ) : selectedProductClass ? (
                // Nivel 2: Líneas dentro de la categoría seleccionada
                (() => {
                  let filteredTemplates: ProductTemplate[] = [];
                  
                  // Filtrar plantillas según la categoría seleccionada
                  switch(selectedProductClass) {
                    case 'VENTANAS':
                      filteredTemplates = templates.filter(t => t.product_class === 'VENTANA');
                      break;
                    case 'PUERTAS':
                      filteredTemplates = templates.filter(t => t.product_class === 'PUERTA');
                      break;
                    case 'PAÑOS FIJOS':
                      filteredTemplates = templates.filter(t => 
                        t.line_name?.toLowerCase().includes('paño fijo') || 
                        t.line_name?.toLowerCase().includes('fijo')
                      );
                      break;
                    case 'ACCESORIOS':
                      filteredTemplates = templates.filter(t => 
                        t.product_class === 'ACCESORIO' || 
                        t.line_name?.toLowerCase().includes('tapajuntas') || 
                        t.line_name?.toLowerCase().includes('premarco')
                      );
                      break;
                    case 'OTROS TIPOS':
                      filteredTemplates = templates.filter(t => 
                        t.line_name?.toLowerCase().includes('banderola') || 
                        t.line_name?.toLowerCase().includes('oscilobatiente') || 
                        t.line_name?.toLowerCase().includes('desplazable')
                      );
                      break;
                    case 'ESPECIALES':
                      filteredTemplates = templates.filter(t => 
                        t.line_name?.toLowerCase().includes('proyectante') || 
                        t.line_name?.toLowerCase().includes('mampara') || 
                        t.line_name?.toLowerCase().includes('postigo') || 
                        t.line_name?.toLowerCase().includes('ventiluz')
                      );
                      break;
                    default:
                      filteredTemplates = [];
                  }
                  
                  const lineGroups = filteredTemplates.reduce((acc: Record<string, ProductTemplate[]>, template) => {
                    const line = template.line_name;
                    if (!acc[line]) acc[line] = [];
                    acc[line].push(template);
                    return acc;
                  }, {});
                  
                  return Object.entries(lineGroups).map(([line, lineTemplates]) => (
                    <tr key={line} className="hover:bg-gray-50 cursor-pointer" onClick={() => setSelectedLine(line)}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {line}
                        </div>
                        <div className="text-sm text-gray-500">
                          {lineTemplates.length} productos
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">
                          LÍNEA
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        Línea
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                          {lineTemplates.length} productos →
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getStatusBadge(lineTemplates.some((t: ProductTemplate) => t.is_active))}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {lineTemplates.filter((t: ProductTemplate) => t.is_active).length} activas
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex justify-end gap-2">
                          <button
                            onClick={(e) => { e.stopPropagation(); onEdit?.(0); }}
                            className="text-blue-600 hover:text-blue-800"
                            title="Nueva plantilla"
                          >
                            <Plus size={16} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ));
                })()
              ) : (
                // Nivel 1: 6 Categorías principales identificadas
                (() => {
                  const categories = [
                    { name: 'VENTANAS', description: '12 plantillas principales', count: templates.filter(t => t.product_class === 'VENTANA').length, color: 'bg-blue-100 text-blue-800' },
                    { name: 'PUERTAS', description: '6 plantillas principales', count: templates.filter(t => t.product_class === 'PUERTA').length, color: 'bg-green-100 text-green-800' },
                    { name: 'PAÑOS FIJOS', description: '5 plantillas', count: templates.filter(t => t.line_name?.toLowerCase().includes('paño fijo') || t.line_name?.toLowerCase().includes('fijo')).length, color: 'bg-purple-100 text-purple-800' },
                    { name: 'ACCESORIOS', description: 'Tapajuntas y Premarcos', count: templates.filter(t => t.product_class === 'ACCESORIO' || t.line_name?.toLowerCase().includes('tapajuntas') || t.line_name?.toLowerCase().includes('premarco')).length, color: 'bg-orange-100 text-orange-800' },
                    { name: 'OTROS TIPOS', description: 'Banderola, Oscilobatiente, etc.', count: templates.filter(t => t.line_name?.toLowerCase().includes('banderola') || t.line_name?.toLowerCase().includes('oscilobatiente') || t.line_name?.toLowerCase().includes('desplazable')).length, color: 'bg-indigo-100 text-indigo-800' },
                    { name: 'ESPECIALES', description: 'Proyectante, Mampara, Postigo', count: templates.filter(t => t.line_name?.toLowerCase().includes('proyectante') || t.line_name?.toLowerCase().includes('mampara') || t.line_name?.toLowerCase().includes('postigo') || t.line_name?.toLowerCase().includes('ventiluz')).length, color: 'bg-pink-100 text-pink-800' }
                  ];
                  
                  return categories.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage).map((category) => (
                    <tr key={category.name} className="hover:bg-gray-50 cursor-pointer" onClick={() => setSelectedProductClass(category.name)}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {category.name}
                        </div>
                        <div className="text-sm text-gray-500">
                          {category.description}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${category.color}`}>
                          {category.name}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        Categoría
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                          {category.count} plantillas →
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getStatusBadge(category.count > 0)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {category.count} disponibles
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex justify-end gap-2">
                          <button
                            onClick={(e) => { e.stopPropagation(); onEdit?.(0); }}
                            className="text-blue-600 hover:text-blue-800"
                            title="Nueva plantilla"
                          >
                            <Plus size={16} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ));
                })()
              )}
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
        
        {selectedLine && (
          <div className="px-6 py-3 border-t bg-blue-50 flex items-center justify-between sticky bottom-0">
            <button
              onClick={() => setSelectedLine(null)}
              className="text-blue-600 hover:text-blue-800 font-medium"
            >
              ← Volver a líneas
            </button>
            <div className="text-sm text-gray-700">
              {selectedProductClass} - {selectedLine}: {templates.filter(t => t.product_class === selectedProductClass && t.line_name === selectedLine).length} productos
            </div>
          </div>
        )}
        
        {selectedProductClass && !selectedLine && (
          <div className="px-6 py-3 border-t bg-blue-50 flex items-center justify-between sticky bottom-0">
            <button
              onClick={() => setSelectedProductClass(null)}
              className="text-blue-600 hover:text-blue-800 font-medium"
            >
              ← Volver a tipos
            </button>
            <div className="text-sm text-gray-700">
              Categoría: {selectedProductClass}
            </div>
          </div>
        )}
        
        {/* Pagination */}
        {!selectedLine && !selectedProductClass && 6 > itemsPerPage && (
          <div className="px-6 py-3 border-t bg-gray-50 flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Mostrando {((currentPage - 1) * itemsPerPage) + 1} a {Math.min(currentPage * itemsPerPage, 6)} de 6 categorías
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                disabled={currentPage === 1}
                className="px-3 py-1 text-sm border rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Anterior
              </button>
              {Array.from({ length: Math.ceil(6 / itemsPerPage) }, (_, i) => i + 1).map(page => (
                <button
                  key={page}
                  onClick={() => setCurrentPage(page)}
                  className={`px-3 py-1 text-sm border rounded ${
                    currentPage === page 
                      ? 'bg-blue-600 text-white border-blue-600' 
                      : 'hover:bg-gray-100'
                  }`}
                >
                  {page}
                </button>
              ))}
              <button
                onClick={() => setCurrentPage(prev => Math.min(prev + 1, Math.ceil(6 / itemsPerPage)))}
                disabled={currentPage === Math.ceil(6 / itemsPerPage)}
                className="px-3 py-1 text-sm border rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Siguiente
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Modal Nueva Plantilla */}
      {showNewTemplateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-96 max-w-md mx-4">
            <h3 className="text-lg font-semibold mb-4">Nueva Plantilla</h3>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nombre de la Plantilla
              </label>
              <input
                type="text"
                value={newTemplateName}
                onChange={(e) => setNewTemplateName(e.target.value)}
                placeholder="Ej: Ventana A30 Corrediza"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                autoFocus
              />
            </div>
            
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => {
                  setShowNewTemplateForm(false);
                  setNewTemplateName('');
                }}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancelar
              </button>
              <button
                onClick={async () => {
                  if (!newTemplateName.trim()) {
                    alert('Por favor ingresa un nombre para la plantilla');
                    return;
                  }
                  
                  try {
                    const response = await fetch('/api/templates/', {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json' },
                      body: JSON.stringify({
                        line_name: newTemplateName,
                        code: newTemplateName.toLowerCase().replace(/\s+/g, '-'),
                        product_class: 'VENTANA',
                        base_price_net: 0,
                        currency: 'ARS',
                        requires_dimensions: true,
                        is_active: true,
                        version: 1
                      })
                    });
                    
                    if (response.ok) {
                      setShowNewTemplateForm(false);
                      setNewTemplateName('');
                      fetchTemplates(); // Recargar la lista
                    } else {
                      alert('Error al crear la plantilla');
                    }
                  } catch (error) {
                    console.error('Error:', error);
                    alert('Error al crear la plantilla');
                  }
                }}
                disabled={!newTemplateName.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Crear Plantilla
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TemplateList;