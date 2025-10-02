import React, { useState, useEffect } from 'react';

interface PricingBreakdown {
  source: string;
  mode: string;
  value: number;
  factor?: number;
  applied_on?: number;
  delta?: number;
  m2?: number;
  m?: number;
  qty?: number;
  unit?: number;
}

interface PricingResult {
  calc: {
    area_m2?: number;
    perimeter_m?: number;
  };
  price: {
    net: number;
    tax: number;
    gross: number;
  };
  breakdown: PricingBreakdown[];
  currency: string;
}

interface TemplateAttribute {
  id: number;
  name: string;
  code: string;
  type: 'SELECT' | 'BOOLEAN' | 'NUMBER' | 'DIMENSIONS_MM' | 'QUANTITY';
  is_required: boolean;
  render_variant: string;
  options: Array<{
    id: number;
    label: string;
    code: string;
    pricing_mode: string;
    price_value: number;
    is_default: boolean;
    swatch_hex?: string;
  }>;
  min_value?: number;
  max_value?: number;
  step_value?: number;
  unit_label?: string;
  min_width?: number;
  max_width?: number;
  min_height?: number;
  max_height?: number;
  step_mm?: number;
}

interface ProductTemplate {
  id: number;
  product_class: string;
  line_name: string;
  code: string;
  base_price_net: number;
  currency: string;
  attributes: TemplateAttribute[];
}

interface TemplatePreviewProps {
  templateId: number;
}

export const TemplatePreview: React.FC<TemplatePreviewProps> = ({ templateId }) => {
  const [template, setTemplate] = useState<ProductTemplate | null>(null);
  const [selections, setSelections] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);

  const fetchTemplate = async () => {
    try {
      const response = await fetch(`/api/templates/${templateId}/`);
      if (response.ok) {
        const data = await response.json();
        setTemplate(data.template);
      }
    } catch (error) {
      console.error('Error fetching template:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTemplate();
  }, [templateId]);

  useEffect(() => {
    if (template) {
      // Set default selections
      const defaults: Record<string, any> = {};
      template.attributes.forEach(attr => {
        if (attr.type === 'SELECT') {
          const defaultOption = attr.options?.find(opt => opt.is_default);
          if (defaultOption) {
            defaults[attr.code] = defaultOption.code;
          } else if (attr.options && attr.options.length > 0) {
            // Si no hay default, usar la primera opción
            defaults[attr.code] = attr.options[0].code;
          }
        } else if (attr.type === 'BOOLEAN') {
          defaults[attr.code] = false;
        } else if (attr.type === 'DIMENSIONS_MM') {
          defaults[attr.code] = {
            width_mm: attr.min_width || 1000,
            height_mm: attr.min_height || 1000
          };
        } else if (attr.type === 'NUMBER' || attr.type === 'QUANTITY') {
          defaults[attr.code] = attr.min_value || 1;
        }
      });
      setSelections(defaults);
    }
  }, [template]);





  const handleSelectionChange = (attrCode: string, value: any) => {
    setSelections(prev => ({
      ...prev,
      [attrCode]: value
    }));
  };

  const renderAttributeInput = (attr: TemplateAttribute) => {
    const value = selections[attr.code];

    switch (attr.type) {
      case 'SELECT':
        if (attr.render_variant === 'swatches') {
          return (
            <div className="flex flex-wrap gap-2">
              {attr.options.map(option => (
                <button
                  key={option.id}
                  onClick={() => handleSelectionChange(attr.code, option.code)}
                  className={`w-8 h-8 rounded border-2 ${
                    value === option.code ? 'border-blue-500' : 'border-gray-300'
                  }`}
                  style={{ backgroundColor: option.swatch_hex || '#ccc' }}
                  title={option.label}
                />
              ))}
            </div>
          );
        }
        return (
          <select
            value={value || ''}
            onChange={(e) => handleSelectionChange(attr.code, e.target.value)}
            className="w-full border rounded px-3 py-2"
          >
            <option value="">Seleccionar...</option>
            {attr.options.map(option => (
              <option key={option.id} value={option.code}>
                {option.label}
              </option>
            ))}
          </select>
        );

      case 'BOOLEAN':
        return (
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={value || false}
              onChange={(e) => handleSelectionChange(attr.code, e.target.checked)}
              className="mr-2"
            />
            {value ? 'Sí' : 'No'}
          </label>
        );

      case 'DIMENSIONS_MM':
        return (
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="block text-xs text-gray-600">Ancho (mm)</label>
              <input
                type="number"
                value={value?.width_mm || ''}
                onChange={(e) => handleSelectionChange(attr.code, {
                  ...value,
                  width_mm: Number(e.target.value)
                })}
                min={attr.min_width}
                max={attr.max_width}
                step={attr.step_mm}
                className="w-full border rounded px-2 py-1"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-600">Alto (mm)</label>
              <input
                type="number"
                value={value?.height_mm || ''}
                onChange={(e) => handleSelectionChange(attr.code, {
                  ...value,
                  height_mm: Number(e.target.value)
                })}
                min={attr.min_height}
                max={attr.max_height}
                step={attr.step_mm}
                className="w-full border rounded px-2 py-1"
              />
            </div>
          </div>
        );

      case 'NUMBER':
      case 'QUANTITY':
        return (
          <div>
            <input
              type="number"
              value={value || ''}
              onChange={(e) => handleSelectionChange(attr.code, Number(e.target.value))}
              min={attr.min_value}
              max={attr.max_value}
              step={attr.step_value}
              className="w-full border rounded px-3 py-2"
            />
            {attr.unit_label && (
              <span className="text-xs text-gray-600 ml-1">{attr.unit_label}</span>
            )}
          </div>
        );

      default:
        return <div>Tipo no soportado</div>;
    }
  };

  if (loading) {
    return <div className="p-6 text-center">Cargando plantilla...</div>;
  }

  if (!template) {
    return <div className="p-6 text-center text-red-600">Error al cargar plantilla</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-full mx-auto space-y-4">
        {/* Configuration Panel */}
        <div className="bg-white rounded-lg shadow-lg border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50">
            <h2 className="text-2xl font-bold text-gray-800">
              {template.product_class} - {template.line_name}
            </h2>
            <p className="text-gray-600 mt-1">Configurador de producto</p>
          </div>

          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {template.attributes.map(attr => (
                <div key={attr.id} className="space-y-2">
                  <label className="block text-sm font-semibold text-gray-700">
                    {attr.name}
                    {attr.is_required && <span className="text-red-500 ml-1">*</span>}
                  </label>
                  <div className="w-full">
                    {renderAttributeInput(attr)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
        
        {/* Related Products */}
        <div className="bg-white rounded-lg shadow-lg border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-green-50 to-emerald-50">
            <h3 className="text-xl font-bold text-gray-800">
              Productos Relacionados - {template.line_name}
            </h3>
          </div>
          <div className="p-6">
            <RelatedProducts lineName={template.line_name} currentTemplateId={template.id} />
          </div>
        </div>
      </div>
    </div>
  );
};

// Componente para productos asociados
interface AssociatedProduct {
  id: number;
  product_class: string;
  line_name: string;
  code: string;
  base_price_net: number;
  currency: string;
  relationship_type: string;
}

interface AssociatedProductsData {
  main_product: {
    id: number;
    product_class: string;
    line_name: string;
    code: string;
  };
  associated_products: AssociatedProduct[];
}

const RelatedProducts: React.FC<{ lineName: string; currentTemplateId: number }> = ({ lineName, currentTemplateId }) => {
  const [associatedData, setAssociatedData] = useState<AssociatedProductsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAssociatedProducts = async () => {
      try {
        const response = await fetch(`/catalog/api/templates/${currentTemplateId}/associated/`);
        if (response.ok) {
          const data = await response.json();
          setAssociatedData(data);
        }
      } catch (error) {
        console.error('Error fetching associated products:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAssociatedProducts();
  }, [currentTemplateId]);

  if (loading) {
    return <div className="text-sm text-gray-500">Cargando productos relacionados...</div>;
  }

  if (!associatedData || associatedData.associated_products.length === 0) {
    return <div className="text-sm text-gray-500">No hay productos asociados</div>;
  }



  const getClassBadge = (productClass: string) => {
    const colors: Record<string, string> = {
      'VENTANA': 'bg-blue-100 text-blue-800',
      'PUERTA': 'bg-green-100 text-green-800',
      'PANO_FIJO': 'bg-purple-100 text-purple-800',
      'ACCESORIO': 'bg-orange-100 text-orange-800'
    };
    
    return (
      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${colors[productClass] || 'bg-gray-100 text-gray-800'}`}>
        {productClass}
      </span>
    );
  };
  
  const getRelationshipBadge = (relationshipType: string) => {
    const colors: Record<string, string> = {
      'ACCESORIO_LINEA': 'bg-yellow-100 text-yellow-800',
      'COMPLEMENTARIO': 'bg-green-100 text-green-800'
    };
    
    const labels: Record<string, string> = {
      'ACCESORIO_LINEA': 'Accesorio',
      'COMPLEMENTARIO': 'Complementario'
    };
    
    return (
      <span className={`inline-flex px-2 py-1 text-xs font-medium rounded ${colors[relationshipType] || 'bg-gray-100 text-gray-800'}`}>
        {labels[relationshipType] || relationshipType}
      </span>
    );
  };

  return (
    <div className="w-full">
      <div className="overflow-x-auto shadow-sm rounded-lg border border-gray-200">
        <table className="w-full text-sm bg-white">
          <thead className="bg-gray-50">
            <tr>
              <th className="text-left py-4 px-6 font-semibold text-gray-700 border-b">Tipo / Relación</th>
              <th className="text-left py-4 px-6 font-semibold text-gray-700 border-b">Código</th>
              <th className="text-right py-4 px-6 font-semibold text-gray-700 border-b">Precio Base</th>
              <th className="text-center py-4 px-6 font-semibold text-gray-700 border-b">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {associatedData.associated_products.map((product) => (
              <tr key={product.id} className="hover:bg-blue-50 transition-colors duration-150">
                <td className="py-4 px-6">
                  <div className="flex flex-col gap-1">
                    {getClassBadge(product.product_class)}
                    {getRelationshipBadge(product.relationship_type)}
                  </div>
                </td>
                <td className="py-4 px-6 font-medium text-gray-900">
                  {product.code.split('-').slice(-2).join('-')}
                </td>
                <td className="py-4 px-6 text-right font-semibold text-gray-700">
                  ${product.base_price_net.toLocaleString()}
                </td>
                <td className="py-4 px-6 text-center">
                  <a 
                    href={`#/plantillas/${product.id}/preview`}
                    className="inline-flex items-center px-3 py-1 rounded-md text-sm font-medium bg-blue-100 text-blue-700 hover:bg-blue-200 transition-colors duration-150"
                  >
                    Ver Detalle
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {associatedData.associated_products.length > 0 && (
        <div className="text-sm text-gray-500 text-center mt-4 py-2">
          {associatedData.associated_products.length} productos asociados encontrados
        </div>
      )}
    </div>
  );
};

export default TemplatePreview;