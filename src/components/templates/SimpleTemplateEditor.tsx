import React, { useState, useEffect } from 'react';

interface Props {
  templateId?: string;
}

interface Attribute {
  id: number;
  name: string;
  code: string;
  type: string;
  is_required: boolean;
  options?: any[];
}

interface Template {
  product_class: string;
  line_name: string;
  code: string;
  currency: string;
  requires_dimensions: boolean;
  is_active: boolean;
  version?: number;
}

const SimpleTemplateEditor: React.FC<Props> = ({ templateId }) => {
  const isNew = templateId === 'new' || !templateId;
  const [template, setTemplate] = useState<Template>({
    product_class: 'VENTANA',
    line_name: '',
    code: '',
    currency: 'ARS',
    requires_dimensions: true,
    is_active: true
  });
  const [loading, setLoading] = useState(!isNew);
  const [saving, setSaving] = useState(false);
  const [attributes, setAttributes] = useState<Attribute[]>([]);
  const [showAddAttribute, setShowAddAttribute] = useState(false);
  const [newAttribute, setNewAttribute] = useState({
    name: '',
    code: '',
    type: 'SELECT',
    is_required: true
  });
  const [selectedAttribute, setSelectedAttribute] = useState<Attribute | null>(null);
  const [showOptions, setShowOptions] = useState(false);
  const [newOption, setNewOption] = useState({
    label: '',
    code: '',
    pricing_mode: 'ABS',
    price_value: '0',
    is_default: false
  });

  useEffect(() => {
    if (!isNew && templateId) {
      fetchTemplate(parseInt(templateId));
    }
  }, [templateId, isNew]);

  const fetchTemplate = async (id: number) => {
    try {
      const response = await fetch(`/api/templates/${id}/`);
      if (response.ok) {
        const data = await response.json();
        setTemplate(data);
        setAttributes(data.attributes || []);
      }
    } catch (error) {
      console.error('Error fetching template:', error);
    } finally {
      setLoading(false);
    }
  };

  const saveTemplate = async () => {
    setSaving(true);
    try {
      const url = isNew ? '/api/templates/' : `/api/templates/${templateId}/`;
      const method = isNew ? 'POST' : 'PATCH';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(template)
      });

      if (response.ok) {
        const savedTemplate = await response.json();
        if (isNew) {
          window.location.hash = `/plantillas/${savedTemplate.id}`;
        } else {
          setTemplate(savedTemplate);
        }
        alert('Plantilla guardada exitosamente');
        if (isNew && savedTemplate.attributes) {
          setAttributes(savedTemplate.attributes);
        }
      } else {
        const errorData = await response.json().catch(() => ({}));
        console.error('Error response:', errorData);
        alert(`Error al guardar: ${errorData.detail || response.statusText}`);
      }
    } catch (error) {
      console.error('Error saving template:', error);
      alert('Error de conexión al guardar la plantilla');
    } finally {
      setSaving(false);
    }
  };

  const addAttribute = async () => {
    try {
      const response = await fetch('/api/attributes/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          ...newAttribute,
          template_id: templateId
        })
      });

      if (response.ok) {
        const savedAttribute = await response.json();
        setAttributes(prev => [...prev, { ...savedAttribute, options: [] }]);
        setNewAttribute({ name: '', code: '', type: 'SELECT', is_required: true });
        setShowAddAttribute(false);
        alert('Atributo agregado exitosamente');
      } else {
        alert('Error al agregar atributo');
      }
    } catch (error) {
      console.error('Error adding attribute:', error);
      alert('Error al agregar atributo');
    }
  };

  const editAttribute = (attribute: Attribute) => {
    if (attribute.type === 'BOOLEAN' || attribute.type === 'NUMBER') {
      alert(`Los atributos de tipo ${attribute.type} no requieren opciones`);
      return;
    }
    setSelectedAttribute(attribute);
    setShowOptions(true);
  };

  const addOption = async () => {
    if (!selectedAttribute) return;

    try {
      const response = await fetch('/api/options/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          ...newOption,
          attribute_id: selectedAttribute.id
        })
      });

      if (response.ok) {
        const savedOption = await response.json();
        setAttributes(prev => prev.map(attr => 
          attr.id === selectedAttribute.id 
            ? { ...attr, options: [...(attr.options || []), savedOption] }
            : attr
        ));
        setNewOption({ label: '', code: '', pricing_mode: 'ABS', price_value: '0', is_default: false });
        alert('Opción agregada exitosamente');
      } else {
        alert('Error al agregar opción');
      }
    } catch (error) {
      console.error('Error adding option:', error);
      alert('Error al agregar opción');
    }
  };

  const deleteOption = async (optionId: number) => {
    if (!window.confirm('¿Está seguro de eliminar esta opción?')) return;

    try {
      const response = await fetch(`/api/options/${optionId}/`, {
        method: 'DELETE',
        credentials: 'include'
      });

      if (response.ok) {
        setAttributes(prev => prev.map(attr => 
          attr.id === selectedAttribute?.id 
            ? { ...attr, options: (attr.options || []).filter(opt => opt.id !== optionId) }
            : attr
        ));
        alert('Opción eliminada exitosamente');
      } else {
        alert('Error al eliminar opción');
      }
    } catch (error) {
      console.error('Error deleting option:', error);
      alert('Error al eliminar opción');
    }
  };

  const deleteAttribute = async (attributeId: number) => {
    if (!window.confirm('¿Está seguro de eliminar este atributo?')) return;

    try {
      const response = await fetch(`/api/attributes/${attributeId}/`, {
        method: 'DELETE',
        credentials: 'include'
      });

      if (response.ok) {
        setAttributes(prev => prev.filter(attr => attr.id !== attributeId));
        alert('Atributo eliminado exitosamente');
      } else {
        alert('Error al eliminar atributo');
      }
    } catch (error) {
      console.error('Error deleting attribute:', error);
      alert('Error al eliminar atributo');
    }
  };

  if (loading) {
    return <div className="flex justify-center p-8">Cargando...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => window.location.hash = '/plantillas'}
                className="text-gray-400 hover:text-gray-600"
              >
                ← Volver
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  {isNew ? 'Nueva Plantilla' : template.line_name}
                </h1>
                <p className="text-sm text-gray-500">
                  {isNew ? 'Crear nueva plantilla de producto' : `Editando plantilla • Versión ${template.version || 1}`}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={() => window.location.hash = '/plantillas'}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Cancelar
              </button>
              <button
                onClick={saveTemplate}
                disabled={saving}
                className="px-4 py-2 bg-blue-600 border border-transparent rounded-md text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {saving ? 'Guardando...' : 'Guardar plantilla'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Información Básica */}
            <div className="bg-white shadow rounded-lg">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-medium text-gray-900">Información Básica</h2>
                <p className="text-sm text-gray-500">Configuración principal de la plantilla</p>
              </div>
              <div className="px-6 py-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Clase de Producto</label>
                    <select
                      value={template.product_class}
                      onChange={(e) => setTemplate(prev => ({ ...prev, product_class: e.target.value }))}
                      className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="VENTANA">Ventana</option>
                      <option value="PUERTA">Puerta</option>
                      <option value="ACCESORIO">Accesorio</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Línea</label>
                    <select
                      value={template.line_name}
                      onChange={(e) => setTemplate(prev => ({ ...prev, line_name: e.target.value }))}
                      className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="">Seleccionar línea...</option>
                      <option value="Módena">Módena</option>
                      <option value="Herrero">Herrero</option>
                      <option value="Línea A30">Línea A30</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Código</label>
                    <input
                      type="text"
                      value={template.code}
                      onChange={(e) => setTemplate(prev => ({ ...prev, code: e.target.value }))}
                      className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Ej: ventana-modena"
                    />
                  </div>

                  <div className="md:col-span-3">
                    <div className="flex items-center space-x-6">
                      <label className="flex items-center">
                        <input
                          type="checkbox"
                          checked={template.requires_dimensions}
                          onChange={(e) => setTemplate(prev => ({ ...prev, requires_dimensions: e.target.checked }))}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <span className="ml-2 text-sm text-gray-700">Requiere dimensiones</span>
                      </label>
                      <label className="flex items-center">
                        <input
                          type="checkbox"
                          checked={template.is_active}
                          onChange={(e) => setTemplate(prev => ({ ...prev, is_active: e.target.checked }))}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <span className="ml-2 text-sm text-gray-700">Activo</span>
                      </label>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Atributos */}
            {!isNew && (
              <div className="bg-white shadow rounded-lg">
                <div className="px-6 py-4 border-b border-gray-200">
                  <div className="flex justify-between items-center">
                    <div>
                      <h2 className="text-lg font-medium text-gray-900">Atributos</h2>
                      <p className="text-sm text-gray-500">Configuración de atributos y opciones</p>
                    </div>
                    <button
                      onClick={() => setShowAddAttribute(true)}
                      className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                      + Agregar Atributo
                    </button>
                  </div>
                </div>
                <div className="px-6 py-4">
                  {attributes.length === 0 ? (
                    <div className="text-center py-8">
                      <div className="text-gray-400 text-sm mb-2">
                        No hay atributos definidos
                      </div>
                      <p className="text-gray-500 text-sm">
                        Los atributos permiten configurar opciones como color, tamaño, etc.
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {attributes.map((attr) => (
                        <div key={attr.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                          <div className="flex items-center space-x-3">
                            <div className="flex-shrink-0">
                              <div className={`w-3 h-3 rounded-full ${
                                attr.type === 'SELECT' ? 'bg-blue-400' :
                                attr.type === 'BOOLEAN' ? 'bg-green-400' :
                                attr.type === 'NUMBER' ? 'bg-yellow-400' :
                                'bg-purple-400'
                              }`}></div>
                            </div>
                            <div>
                              <div className="flex items-center space-x-2">
                                <span className="font-medium text-gray-900">{attr.name}</span>
                                {attr.is_required && (
                                  <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                                    Obligatorio
                                  </span>
                                )}
                              </div>
                              <div className="text-sm text-gray-500">
                                {attr.code} • {attr.type} • {attr.options?.length || 0} opciones
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={() => editAttribute(attr)}
                              className={`inline-flex items-center px-3 py-1 border text-sm font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 ${
                                attr.type === 'SELECT' || attr.type === 'COLOR'
                                  ? 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50 focus:ring-blue-500'
                                  : 'border-gray-200 text-gray-400 bg-gray-50 cursor-not-allowed'
                              }`}
                              disabled={attr.type === 'BOOLEAN' || attr.type === 'NUMBER'}
                            >
                              {attr.type === 'SELECT' || attr.type === 'COLOR' ? 'Gestionar Opciones' : 'Sin opciones'}
                            </button>
                            <button
                              onClick={() => deleteAttribute(attr.id)}
                              className="inline-flex items-center px-3 py-1 border border-red-300 text-sm font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                            >
                              Eliminar
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Información</h3>
              <div className="space-y-4 text-sm">
                <div>
                  <span className="text-gray-500">Estado:</span>
                  <span className={`ml-2 inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                    template.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {template.is_active ? 'Activa' : 'Inactiva'}
                  </span>
                </div>
                {!isNew && (
                  <>
                    <div>
                      <span className="text-gray-500">Versión:</span>
                      <span className="ml-2 text-gray-900">{template.version || 1}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Atributos:</span>
                      <span className="ml-2 text-gray-900">{attributes.length}</span>
                    </div>
                  </>
                )}
                <div>
                  <span className="text-gray-500">Dimensiones:</span>
                  <span className="ml-2 text-gray-900">
                    {template.requires_dimensions ? 'Requeridas' : 'No requeridas'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Modal para agregar atributo */}
      {showAddAttribute && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">Nuevo Atributo</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Nombre</label>
                <input
                  type="text"
                  value={newAttribute.name}
                  onChange={(e) => setNewAttribute(prev => ({ ...prev, name: e.target.value }))}
                  className="w-full border rounded px-3 py-2"
                  placeholder="Ej: Color"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Código</label>
                <input
                  type="text"
                  value={newAttribute.code}
                  onChange={(e) => setNewAttribute(prev => ({ ...prev, code: e.target.value }))}
                  className="w-full border rounded px-3 py-2"
                  placeholder="Ej: color"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Tipo</label>
                <select
                  value={newAttribute.type}
                  onChange={(e) => setNewAttribute(prev => ({ ...prev, type: e.target.value }))}
                  className="w-full border rounded px-3 py-2"
                >
                  <option value="SELECT">Select</option>
                  <option value="BOOLEAN">Boolean</option>
                  <option value="NUMBER">Number</option>
                  <option value="COLOR">Color</option>
                </select>
              </div>
              <div>
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={newAttribute.is_required}
                    onChange={(e) => setNewAttribute(prev => ({ ...prev, is_required: e.target.checked }))}
                  />
                  <span className="text-sm font-medium">Obligatorio</span>
                </label>
              </div>
            </div>
            <div className="flex justify-end space-x-2 mt-6">
              <button
                onClick={() => setShowAddAttribute(false)}
                className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-50"
              >
                Cancelar
              </button>
              <button
                onClick={addAttribute}
                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
              >
                Agregar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal para gestionar opciones */}
      {showOptions && selectedAttribute && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Opciones: {selectedAttribute.name}</h3>
              <button
                onClick={() => setShowOptions(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ×
              </button>
            </div>

            {/* Lista de opciones existentes */}
            <div className="mb-6">
              <h4 className="font-medium mb-2">Opciones existentes:</h4>
              {selectedAttribute.options && selectedAttribute.options.length > 0 ? (
                <div className="space-y-2">
                  {selectedAttribute.options.map((option: any) => (
                    <div key={option.id} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                      <div>
                        <span className="font-medium">{option.label}</span>
                        <span className="text-sm text-gray-500 ml-2">({option.code})</span>
                        <span className="text-sm text-blue-600 ml-2">${option.price_value}</span>
                      </div>
                      <button
                        onClick={() => deleteOption(option.id)}
                        className="text-red-600 hover:text-red-800 text-sm"
                      >
                        Eliminar
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-sm">No hay opciones definidas</p>
              )}
            </div>

            {/* Formulario para nueva opción */}
            <div className="border-t pt-4">
              <h4 className="font-medium mb-3">Agregar nueva opción:</h4>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Etiqueta</label>
                  <input
                    type="text"
                    value={newOption.label}
                    onChange={(e) => setNewOption(prev => ({ ...prev, label: e.target.value }))}
                    className="w-full border rounded px-3 py-2"
                    placeholder="Ej: Blanco"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Código</label>
                  <input
                    type="text"
                    value={newOption.code}
                    onChange={(e) => setNewOption(prev => ({ ...prev, code: e.target.value }))}
                    className="w-full border rounded px-3 py-2"
                    placeholder="Ej: blanco"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Modo de Precio</label>
                  <select
                    value={newOption.pricing_mode}
                    onChange={(e) => setNewOption(prev => ({ ...prev, pricing_mode: e.target.value }))}
                    className="w-full border rounded px-3 py-2"
                  >
                    <option value="ABS">Suma absoluta</option>
                    <option value="FACTOR">Factor multiplicativo</option>
                    <option value="PER_M2">Precio por m²</option>
                    <option value="PERIMETER">Precio por perímetro</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Valor</label>
                  <input
                    type="number"
                    step="0.01"
                    value={newOption.price_value}
                    onChange={(e) => setNewOption(prev => ({ ...prev, price_value: e.target.value }))}
                    className="w-full border rounded px-3 py-2"
                  />
                </div>
              </div>
              <div className="mt-3">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={newOption.is_default}
                    onChange={(e) => setNewOption(prev => ({ ...prev, is_default: e.target.checked }))}
                  />
                  <span className="text-sm font-medium">Opción por defecto</span>
                </label>
              </div>
              <div className="flex justify-end space-x-2 mt-4">
                <button
                  onClick={addOption}
                  className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
                >
                  Agregar Opción
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SimpleTemplateEditor;