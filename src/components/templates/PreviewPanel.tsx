import React, { useState, useEffect } from 'react';

interface Template {
  id?: number;
  product_class: string;
  line_name: string;
  code: string;
  base_price_net: string;
  currency: string;
  requires_dimensions: boolean;
  is_active: boolean;
  attributes: Attribute[];
}

interface Attribute {
  id?: number;
  name: string;
  code: string;
  type: string;
  is_required: boolean;
  order: number;
  rules_json: any;
  options: Option[];
}

interface Option {
  id?: number;
  label: string;
  code: string;
  pricing_mode: string;
  price_value: string;
  currency: string;
  order: number;
  is_default: boolean;
}

interface PreviewResult {
  calc: {
    area_m2: number;
    perimeter_m: number;
  };
  price: {
    net: number;
    tax: number;
    gross: number;
  };
  breakdown: Array<{
    source: string;
    mode: string;
    value?: number;
    factor?: number;
    applied_on?: number;
    delta?: number;
    m2?: number;
    perimeter_m?: number;
    unit?: number;
  }>;
  currency: string;
}

interface Props {
  template: Template;
}

const PreviewPanel: React.FC<Props> = ({ template }) => {
  const [selections, setSelections] = useState<Record<string, any>>({});
  const [dimensions, setDimensions] = useState({
    width_mm: 1300,
    height_mm: 1200
  });
  const [previewResult, setPreviewResult] = useState<PreviewResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Inicializar selecciones con valores por defecto
  useEffect(() => {
    const defaultSelections: Record<string, any> = {};
    
    template.attributes.forEach(attr => {
      if (attr.type === 'BOOLEAN') {
        defaultSelections[attr.code] = false;
      } else {
        const defaultOption = attr.options.find(opt => opt.is_default);
        if (defaultOption) {
          defaultSelections[attr.code] = defaultOption.code;
        }
      }
    });
    
    setSelections(defaultSelections);
  }, [template.attributes]);

  // Calcular preview automáticamente cuando cambian las selecciones
  useEffect(() => {
    if (Object.keys(selections).length > 0) {
      calculatePreview();
    }
  }, [selections, dimensions]);

  const calculatePreview = async () => {
    if (!template.id) return;

    setLoading(true);
    setError(null);

    try {
      const payload: any = {
        selections,
        currency: 'ARS',
        iva_pct: 21.0
      };

      if (template.requires_dimensions) {
        payload.width_mm = dimensions.width_mm;
        payload.height_mm = dimensions.height_mm;
      }

      const response = await fetch(`/api/templates/${template.id}/preview_pricing/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        const result = await response.json();
        setPreviewResult(result);
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Error al calcular el precio');
      }
    } catch (err) {
      setError('Error de conexión');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectionChange = (attrCode: string, value: any) => {
    setSelections(prev => ({
      ...prev,
      [attrCode]: value
    }));
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-AR', {
      style: 'currency',
      currency: 'ARS'
    }).format(amount);
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h2 className="text-lg font-semibold mb-4">Preview de Precio</h2>

      {/* Dimensiones */}
      {template.requires_dimensions && (
        <div className="mb-4">
          <h3 className="font-medium mb-2">Dimensiones</h3>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="block text-xs font-medium mb-1">Ancho (mm)</label>
              <input
                type="number"
                value={dimensions.width_mm}
                onChange={(e) => setDimensions(prev => ({ 
                  ...prev, 
                  width_mm: parseInt(e.target.value) || 0 
                }))}
                className="w-full border rounded px-2 py-1 text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium mb-1">Alto (mm)</label>
              <input
                type="number"
                value={dimensions.height_mm}
                onChange={(e) => setDimensions(prev => ({ 
                  ...prev, 
                  height_mm: parseInt(e.target.value) || 0 
                }))}
                className="w-full border rounded px-2 py-1 text-sm"
              />
            </div>
          </div>
        </div>
      )}

      {/* Selecciones */}
      <div className="mb-4">
        <h3 className="font-medium mb-2">Selecciones</h3>
        <div className="space-y-3">
          {template.attributes.map(attr => (
            <div key={attr.code}>
              <label className="block text-xs font-medium mb-1">
                {attr.name}
                {attr.is_required && <span className="text-red-500">*</span>}
              </label>
              
              {attr.type === 'BOOLEAN' ? (
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={selections[attr.code] || false}
                    onChange={(e) => handleSelectionChange(attr.code, e.target.checked)}
                  />
                  <span className="text-sm">Sí</span>
                </label>
              ) : (
                <select
                  value={selections[attr.code] || ''}
                  onChange={(e) => handleSelectionChange(attr.code, e.target.value)}
                  className="w-full border rounded px-2 py-1 text-sm"
                >
                  <option value="">Seleccionar...</option>
                  {attr.options.map(option => (
                    <option key={option.code} value={option.code}>
                      {option.label}
                    </option>
                  ))}
                </select>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Resultado */}
      {loading && (
        <div className="text-center py-4 text-gray-500">
          Calculando...
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded p-3 mb-4">
          <p className="text-red-600 text-sm">{error}</p>
        </div>
      )}

      {previewResult && !loading && (
        <div>
          <h3 className="font-medium mb-2">Resultado</h3>
          
          {/* Cálculos */}
          {template.requires_dimensions && (
            <div className="bg-gray-50 p-3 rounded mb-3">
              <div className="text-sm space-y-1">
                <div>Área: {previewResult.calc.area_m2} m²</div>
                <div>Perímetro: {previewResult.calc.perimeter_m} m</div>
              </div>
            </div>
          )}

          {/* Precios */}
          <div className="bg-blue-50 p-3 rounded mb-3">
            <div className="space-y-1">
              <div className="flex justify-between">
                <span className="text-sm">Precio Neto:</span>
                <span className="font-medium">{formatCurrency(previewResult.price.net)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">IVA (21%):</span>
                <span className="text-sm">{formatCurrency(previewResult.price.tax)}</span>
              </div>
              <div className="flex justify-between border-t pt-1">
                <span className="font-medium">Total:</span>
                <span className="font-bold">{formatCurrency(previewResult.price.gross)}</span>
              </div>
            </div>
          </div>

          {/* Breakdown */}
          <div>
            <h4 className="text-sm font-medium mb-2">Detalle del Cálculo</h4>
            <div className="space-y-1">
              {previewResult.breakdown.map((item, index) => (
                <div key={index} className="text-xs bg-gray-50 p-2 rounded">
                  <div className="font-medium">{item.source}</div>
                  <div className="text-gray-600">
                    {item.mode === 'ABS' && `Suma: ${formatCurrency(item.value || 0)}`}
                    {item.mode === 'PER_M2' && `${item.unit} × ${item.m2} m² = ${formatCurrency(item.value || 0)}`}
                    {item.mode === 'PERIMETER' && `${item.unit} × ${item.perimeter_m} m = ${formatCurrency(item.value || 0)}`}
                    {item.mode === 'FACTOR' && `${formatCurrency(item.applied_on || 0)} × ${item.factor} = +${formatCurrency(item.delta || 0)}`}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PreviewPanel;