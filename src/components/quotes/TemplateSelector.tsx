import React, { useState, useEffect } from 'react';

interface Template {
  id: number;
  product_class: string;
  line_name: string;
  code: string;
  requires_dimensions: boolean;
  attributes: Attribute[];
}

interface Attribute {
  id: number;
  name: string;
  code: string;
  type: string;
  is_required: boolean;
  options: Option[];
}

interface Option {
  id: number;
  label: string;
  code: string;
  pricing_mode: string;
  price_value: string;
  is_default: boolean;
}

interface Props {
  onAddItem: (itemData: any) => void;
  onCancel: () => void;
}

const TemplateSelector: React.FC<Props> = ({ onAddItem, onCancel }) => {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);
  const [selections, setSelections] = useState<Record<string, any>>({});
  const [dimensions, setDimensions] = useState({
    width_mm: '',
    height_mm: ''
  });
  const [quantity, setQuantity] = useState('1');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      const response = await fetch('/api/templates/');
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

  const handleTemplateSelect = (template: Template) => {
    setSelectedTemplate(template);
    // Inicializar selecciones con valores por defecto
    const defaultSelections: Record<string, any> = {};
    template.attributes?.forEach(attr => {
      if (attr.type === 'BOOLEAN') {
        defaultSelections[attr.code] = false;
      } else {
        const defaultOption = attr.options?.find(opt => opt.is_default);
        if (defaultOption) {
          defaultSelections[attr.code] = defaultOption.code;
        }
      }
    });
    setSelections(defaultSelections);
  };

  const handleSelectionChange = (attributeCode: string, value: any) => {
    setSelections(prev => ({
      ...prev,
      [attributeCode]: value
    }));
  };

  const calculatePreview = async () => {
    if (!selectedTemplate) return null;

    try {
      const response = await fetch(`/api/templates/${selectedTemplate.id}/preview_pricing/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          selections,
          width_mm: selectedTemplate.requires_dimensions ? parseInt(dimensions.width_mm) : undefined,
          height_mm: selectedTemplate.requires_dimensions ? parseInt(dimensions.height_mm) : undefined,
          currency: 'ARS',
          iva_pct: 21.0
        })
      });

      if (response.ok) {
        const data = await response.json();
        return data;
      }
    } catch (error) {
      console.error('Error calculating preview:', error);
    }
    return null;
  };

  const handleAddToQuote = async () => {
    const preview = await calculatePreview();
    if (!preview || !selectedTemplate) return;

    const itemData = {
      template_id: selectedTemplate.id,
      template_name: selectedTemplate.line_name,
      selections,
      dimensions: selectedTemplate.requires_dimensions ? dimensions : null,
      quantity: parseFloat(quantity),
      unit_price: preview.price.net,
      tax_rate: 21.0,
      description: `${selectedTemplate.line_name} - ${selectedTemplate.product_class}`,
      breakdown: preview.breakdown
    };

    onAddItem(itemData);
  };

  const isFormValid = () => {
    if (!selectedTemplate) return false;
    
    // Verificar atributos requeridos
    for (const attr of selectedTemplate.attributes || []) {
      if (attr.is_required && !selections[attr.code]) {
        return false;
      }
    }

    // Verificar dimensiones si son requeridas
    if (selectedTemplate.requires_dimensions) {
      if (!dimensions.width_mm || !dimensions.height_mm) {
        return false;
      }
    }

    return true;
  };

  if (loading) {
    return <div className="flex justify-center p-8">Cargando plantillas...</div>;
  }

  return (
    <div className="space-y-6">
      {!selectedTemplate ? (
        // Selector de plantillas
        <div>
          <h3 className="text-lg font-semibold mb-4">Seleccionar Plantilla</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-96 overflow-y-auto">
            {templates.map((template) => (
              <div
                key={template.id}
                onClick={() => handleTemplateSelect(template)}
                className="p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 cursor-pointer transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-gray-900">{template.line_name}</h4>
                    <p className="text-sm text-gray-500">{template.product_class}</p>
                    <p className="text-xs text-gray-400">{template.code}</p>
                  </div>
                  <div className="text-right">
                    <span className="text-xs text-gray-500">
                      {template.attributes?.length || 0} atributos
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
          {templates.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              No hay plantillas disponibles
            </div>
          )}
        </div>
      ) : (
        // Configurador de plantilla
        <div>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold">{selectedTemplate.line_name}</h3>
              <p className="text-sm text-gray-500">{selectedTemplate.product_class}</p>
            </div>
            <button
              onClick={() => setSelectedTemplate(null)}
              className="text-blue-600 hover:text-blue-800 text-sm"
            >
              Cambiar plantilla
            </button>
          </div>

          <div className="space-y-6">
            {/* Dimensiones */}
            {selectedTemplate.requires_dimensions && (
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-medium mb-3">Dimensiones</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">Ancho (mm)</label>
                    <input
                      type="number"
                      value={dimensions.width_mm}
                      onChange={(e) => setDimensions(prev => ({ ...prev, width_mm: e.target.value }))}
                      className="w-full border rounded px-3 py-2"
                      placeholder="1300"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Alto (mm)</label>
                    <input
                      type="number"
                      value={dimensions.height_mm}
                      onChange={(e) => setDimensions(prev => ({ ...prev, height_mm: e.target.value }))}
                      className="w-full border rounded px-3 py-2"
                      placeholder="1200"
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Atributos */}
            {selectedTemplate.attributes?.map((attribute) => (
              <div key={attribute.id} className="bg-white border rounded-lg p-4">
                <div className="flex items-center mb-3">
                  <h4 className="font-medium">{attribute.name}</h4>
                  {attribute.is_required && (
                    <span className="ml-2 text-red-500 text-sm">*</span>
                  )}
                </div>

                {attribute.type === 'BOOLEAN' ? (
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={selections[attribute.code] || false}
                      onChange={(e) => handleSelectionChange(attribute.code, e.target.checked)}
                      className="mr-2"
                    />
                    <span className="text-sm">Incluir {attribute.name}</span>
                  </label>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                    {attribute.options?.map((option) => (
                      <label
                        key={option.id}
                        className={`flex items-center p-3 border rounded cursor-pointer transition-colors ${
                          selections[attribute.code] === option.code
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <input
                          type="radio"
                          name={attribute.code}
                          value={option.code}
                          checked={selections[attribute.code] === option.code}
                          onChange={(e) => handleSelectionChange(attribute.code, e.target.value)}
                          className="mr-2"
                        />
                        <div className="flex-1">
                          <div className="font-medium text-sm">{option.label}</div>
                          <div className="text-xs text-gray-500">
                            {option.pricing_mode === 'ABS' && `+$${parseFloat(option.price_value).toLocaleString()}`}
                            {option.pricing_mode === 'FACTOR' && `×${option.price_value}`}
                            {option.pricing_mode === 'PER_M2' && `$${parseFloat(option.price_value).toLocaleString()}/m²`}
                            {option.pricing_mode === 'PERIMETER' && `$${parseFloat(option.price_value).toLocaleString()}/ml`}
                          </div>
                        </div>
                      </label>
                    ))}
                  </div>
                )}
              </div>
            ))}

            {/* Cantidad */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <label className="block text-sm font-medium mb-2">Cantidad</label>
              <input
                type="number"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                min="1"
                step="1"
                className="w-32 border rounded px-3 py-2"
              />
            </div>
          </div>
        </div>
      )}

      {/* Botones */}
      <div className="flex justify-end gap-3 pt-4 border-t">
        <button
          onClick={onCancel}
          className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
        >
          Cancelar
        </button>
        {selectedTemplate && (
          <button
            onClick={handleAddToQuote}
            disabled={!isFormValid()}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Agregar al Presupuesto
          </button>
        )}
      </div>
    </div>
  );
};

export default TemplateSelector;