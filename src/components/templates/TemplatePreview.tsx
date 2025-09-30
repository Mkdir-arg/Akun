import React, { useState, useEffect } from 'react';
import { Calculator } from 'lucide-react';

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
  const [pricing, setPricing] = useState<PricingResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [calculating, setCalculating] = useState(false);

  useEffect(() => {
    fetchTemplate();
  }, [templateId]);

  useEffect(() => {
    if (template) {
      // Set default selections
      const defaults: Record<string, any> = {};
      template.attributes.forEach(attr => {
        if (attr.type === 'SELECT') {
          const defaultOption = attr.options.find(opt => opt.is_default);
          if (defaultOption) {
            defaults[attr.code] = defaultOption.code;
          }
        } else if (attr.type === 'BOOLEAN') {
          defaults[attr.code] = false;
        } else if (attr.type === 'DIMENSIONS_MM') {
          defaults[attr.code] = {
            width_mm: attr.min_width || 1000,
            height_mm: attr.min_height || 1000
          };
        } else if (attr.type === 'NUMBER' || attr.type === 'QUANTITY') {
          defaults[attr.code] = attr.min_value || 0;
        }
      });
      setSelections(defaults);
    }
  }, [template]);

  useEffect(() => {
    if (template && Object.keys(selections).length > 0) {
      calculatePricing();
    }
  }, [selections, template]);

  const fetchTemplate = async () => {
    try {
      const response = await fetch(`/api/templates/${templateId}/`);
      if (response.ok) {
        const data = await response.json();
        setTemplate(data);
      }
    } catch (error) {
      console.error('Error fetching template:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculatePricing = async () => {
    if (!template) return;

    setCalculating(true);
    try {
      const response = await fetch(`/api/templates/${templateId}/preview_pricing/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          selections,
          currency: 'ARS',
          iva_pct: 21.0
        })
      });

      if (response.ok) {
        const result = await response.json();
        setPricing(result);
      }
    } catch (error) {
      console.error('Error calculating pricing:', error);
    } finally {
      setCalculating(false);
    }
  };

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
    <div className="p-6 max-w-7xl mx-auto">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configuration Panel */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-sm border">
            <div className="p-6 border-b">
              <h2 className="text-xl font-semibold">
                {template.product_class} - {template.line_name}
              </h2>
              <p className="text-gray-600">Configurador de producto</p>
            </div>

            <div className="p-6 space-y-6">
              {template.attributes.map(attr => (
                <div key={attr.id}>
                  <label className="block text-sm font-medium mb-2">
                    {attr.name}
                    {attr.is_required && <span className="text-red-500 ml-1">*</span>}
                  </label>
                  {renderAttributeInput(attr)}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Pricing Panel */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-sm border sticky top-6">
            <div className="p-4 border-b">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <Calculator size={20} />
                Cotización
              </h3>
            </div>

            <div className="p-4">
              {calculating ? (
                <div className="text-center py-4">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                  <p className="text-sm text-gray-600 mt-2">Calculando...</p>
                </div>
              ) : pricing ? (
                <div className="space-y-4">
                  {/* Calculations */}
                  {pricing.calc.area_m2 && (
                    <div className="text-sm">
                      <span className="text-gray-600">Área:</span>
                      <span className="font-medium ml-2">{pricing.calc.area_m2} m²</span>
                    </div>
                  )}
                  {pricing.calc.perimeter_m && (
                    <div className="text-sm">
                      <span className="text-gray-600">Perímetro:</span>
                      <span className="font-medium ml-2">{pricing.calc.perimeter_m} m</span>
                    </div>
                  )}

                  {/* Price Summary */}
                  <div className="border-t pt-4">
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span>Subtotal:</span>
                        <span>${pricing.price.net.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>IVA (21%):</span>
                        <span>${pricing.price.tax.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between font-bold text-lg border-t pt-2">
                        <span>Total:</span>
                        <span>${pricing.price.gross.toLocaleString()}</span>
                      </div>
                    </div>
                  </div>

                  {/* Breakdown */}
                  <div className="border-t pt-4">
                    <h4 className="font-medium mb-2">Desglose:</h4>
                    <div className="space-y-1 text-sm">
                      {pricing.breakdown.map((item, index) => (
                        <div key={index} className="flex justify-between">
                          <span className="text-gray-600">{item.source}:</span>
                          <span>${item.value.toLocaleString()}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-4 text-gray-500">
                  Complete la configuración para ver el precio
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TemplatePreview;