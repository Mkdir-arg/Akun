import React, { useState, useEffect } from 'react';
import { Plus, Edit, Trash2, Move, Settings } from 'lucide-react';

interface AttributeOption {
  id?: number;
  label: string;
  code: string;
  pricing_mode: 'ABS' | 'PER_M2' | 'PERIMETER' | 'FACTOR' | 'PER_UNIT';
  price_value: number;
  currency: string;
  order: number;
  is_default: boolean;
  swatch_hex?: string;
  icon?: string;
  qty_attr_code?: string;
}

interface TemplateAttribute {
  id?: number;
  name: string;
  code: string;
  type: 'SELECT' | 'BOOLEAN' | 'NUMBER' | 'DIMENSIONS_MM' | 'QUANTITY';
  is_required: boolean;
  order: number;
  render_variant: 'select' | 'swatches' | 'radio' | 'buttons';
  rules_json: any;
  min_value?: number;
  max_value?: number;
  step_value?: number;
  unit_label?: string;
  min_width?: number;
  max_width?: number;
  min_height?: number;
  max_height?: number;
  step_mm?: number;
  rebaje_vidrio_mm?: number;
  options: AttributeOption[];
}

interface ProductTemplate {
  id?: number;
  product_class: 'VENTANA' | 'PUERTA' | 'ACCESORIO';
  line_name: string;
  code: string;
  base_price_net: number;
  currency: string;
  requires_dimensions: boolean;
  is_active: boolean;
  version: number;
  attributes: TemplateAttribute[];
}

interface TemplateEditorProps {
  templateId?: number;
  onSave?: (template: ProductTemplate) => void;
}

export const TemplateEditor: React.FC<TemplateEditorProps> = ({ templateId, onSave }) => {
  const [template, setTemplate] = useState<ProductTemplate>({
    product_class: 'VENTANA',
    line_name: '',
    code: '',
    base_price_net: 0,
    currency: 'ARS',
    requires_dimensions: true,
    is_active: true,
    version: 1,
    attributes: []
  });

  const [selectedAttribute, setSelectedAttribute] = useState<TemplateAttribute | null>(null);
  const [showAttributeModal, setShowAttributeModal] = useState(false);
  const [showOptionsModal, setShowOptionsModal] = useState(false);

  useEffect(() => {
    if (templateId) {
      fetchTemplate(templateId);
    }
  }, [templateId]);

  const fetchTemplate = async (id: number) => {
    try {
      const response = await fetch(`/api/templates/${id}/`);
      if (response.ok) {
        const data = await response.json();
        setTemplate(data.template || data);
      }
    } catch (error) {
      console.error('Error fetching template:', error);
    }
  };

  const handleSaveTemplate = async () => {
    try {
      const url = templateId ? `/api/templates/${templateId}/` : '/api/templates/';
      const method = templateId ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(template)
      });

      if (response.ok) {
        const savedTemplate = await response.json();
        onSave?.(savedTemplate);
      }
    } catch (error) {
      console.error('Error saving template:', error);
    }
  };

  const addAttribute = () => {
    setSelectedAttribute({
      name: '',
      code: '',
      type: 'SELECT',
      is_required: true,
      order: template.attributes.length + 1,
      render_variant: 'select',
      rules_json: {},
      options: []
    });
    setShowAttributeModal(true);
  };

  const editAttribute = (attr: TemplateAttribute) => {
    setSelectedAttribute(attr);
    setShowAttributeModal(true);
  };

  const deleteAttribute = (index: number) => {
    const newAttributes = template.attributes.filter((_, i) => i !== index);
    setTemplate({ ...template, attributes: newAttributes });
  };

  const saveAttribute = (attr: TemplateAttribute) => {
    if (selectedAttribute?.id) {
      // Edit existing
      const newAttributes = template.attributes.map(a => 
        a.id === selectedAttribute.id ? attr : a
      );
      setTemplate({ ...template, attributes: newAttributes });
    } else {
      // Add new
      setTemplate({ 
        ...template, 
        attributes: [...template.attributes, { ...attr, id: Date.now() }]
      });
    }
    setShowAttributeModal(false);
    setSelectedAttribute(null);
  };

  const manageOptions = (attr: TemplateAttribute) => {
    if (attr.type !== 'SELECT') {
      alert('Sin opciones disponibles para este tipo de campo');
      return;
    }
    setSelectedAttribute(attr);
    setShowOptionsModal(true);
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-6 border-b">
          <h2 className="text-xl font-semibold">Editor de Plantillas</h2>
        </div>

        {/* Template Info */}
        <div className="p-6 border-b">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Clase de Producto</label>
              <select 
                value={template.product_class}
                onChange={(e) => setTemplate({...template, product_class: e.target.value as any})}
                className="w-full border rounded px-3 py-2"
              >
                <option value="VENTANA">Ventana</option>
                <option value="PUERTA">Puerta</option>
                <option value="ACCESORIO">Accesorio</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Línea</label>
              <input
                type="text"
                value={template.line_name}
                onChange={(e) => setTemplate({...template, line_name: e.target.value})}
                className="w-full border rounded px-3 py-2"
                placeholder="ej: Módena"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Código</label>
              <input
                type="text"
                value={template.code}
                onChange={(e) => setTemplate({...template, code: e.target.value})}
                className="w-full border rounded px-3 py-2"
                placeholder="ej: ventana-modena"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Precio Base</label>
              <input
                type="number"
                value={template.base_price_net}
                onChange={(e) => setTemplate({...template, base_price_net: Number(e.target.value)})}
                className="w-full border rounded px-3 py-2"
              />
            </div>
          </div>
        </div>

        {/* Attributes Table */}
        <div className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-medium">Atributos</h3>
            <button
              onClick={addAttribute}
              className="bg-blue-600 text-white px-4 py-2 rounded flex items-center gap-2"
            >
              <Plus size={16} />
              Agregar Atributo
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full border-collapse border">
              <thead>
                <tr className="bg-gray-50">
                  <th className="border p-2 text-left">Tipo</th>
                  <th className="border p-2 text-left">Nombre</th>
                  <th className="border p-2 text-left">Código</th>
                  <th className="border p-2 text-left">Requerido</th>
                  <th className="border p-2 text-left">Render</th>
                  <th className="border p-2 text-left">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {(template.attributes || []).map((attr, index) => (
                  <tr key={attr.id || index}>
                    <td className="border p-2">{attr.type}</td>
                    <td className="border p-2">{attr.name}</td>
                    <td className="border p-2">{attr.code}</td>
                    <td className="border p-2">{attr.is_required ? 'Sí' : 'No'}</td>
                    <td className="border p-2">{attr.render_variant}</td>
                    <td className="border p-2">
                      <div className="flex gap-2">
                        <button
                          onClick={() => editAttribute(attr)}
                          className="text-blue-600 hover:text-blue-800"
                        >
                          <Edit size={16} />
                        </button>
                        <button
                          onClick={() => manageOptions(attr)}
                          className="text-green-600 hover:text-green-800"
                        >
                          <Settings size={16} />
                        </button>
                        <button
                          onClick={() => deleteAttribute(index)}
                          className="text-red-600 hover:text-red-800"
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
        </div>

        {/* Save Button */}
        <div className="p-6 border-t">
          <button
            onClick={handleSaveTemplate}
            className="bg-green-600 text-white px-6 py-2 rounded"
          >
            Guardar Plantilla
          </button>
        </div>
      </div>

      {/* Modals would go here */}
      {showAttributeModal && (
        <AttributeModal
          attribute={selectedAttribute}
          onSave={saveAttribute}
          onClose={() => setShowAttributeModal(false)}
        />
      )}

      {showOptionsModal && selectedAttribute && (
        <OptionsModal
          attribute={selectedAttribute}
          onClose={() => setShowOptionsModal(false)}
        />
      )}
    </div>
  );
};

// Placeholder components for modals
const AttributeModal: React.FC<{
  attribute: TemplateAttribute | null;
  onSave: (attr: TemplateAttribute) => void;
  onClose: () => void;
}> = ({ attribute, onSave, onClose }) => {
  const [formData, setFormData] = useState<TemplateAttribute>(
    attribute || {
      name: '',
      code: '',
      type: 'SELECT',
      is_required: true,
      order: 1,
      render_variant: 'select',
      rules_json: {},
      options: []
    }
  );

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div className="bg-white p-6 rounded-lg w-96">
        <h3 className="text-lg font-medium mb-4">
          {attribute?.id ? 'Editar' : 'Agregar'} Atributo
        </h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Nombre</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              className="w-full border rounded px-3 py-2"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Código</label>
            <input
              type="text"
              value={formData.code}
              onChange={(e) => setFormData({...formData, code: e.target.value})}
              className="w-full border rounded px-3 py-2"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Tipo</label>
            <select
              value={formData.type}
              onChange={(e) => setFormData({...formData, type: e.target.value as any})}
              className="w-full border rounded px-3 py-2"
            >
              <option value="SELECT">Select</option>
              <option value="BOOLEAN">Boolean</option>
              <option value="NUMBER">Number</option>
              <option value="DIMENSIONS_MM">Dimensions (mm)</option>
              <option value="QUANTITY">Quantity</option>
            </select>
          </div>
        </div>

        <div className="flex gap-2 mt-6">
          <button
            onClick={() => onSave(formData)}
            className="bg-blue-600 text-white px-4 py-2 rounded"
          >
            Guardar
          </button>
          <button
            onClick={onClose}
            className="bg-gray-300 text-gray-700 px-4 py-2 rounded"
          >
            Cancelar
          </button>
        </div>
      </div>
    </div>
  );
};

const OptionsModal: React.FC<{
  attribute: TemplateAttribute;
  onClose: () => void;
}> = ({ attribute, onClose }) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div className="bg-white p-6 rounded-lg w-4/5 max-w-4xl">
        <h3 className="text-lg font-medium mb-4">
          Gestionar Opciones - {attribute.name}
        </h3>
        
        <div className="text-center py-8 text-gray-500">
          {attribute.type === 'SELECT' 
            ? 'Tabla de opciones aquí...' 
            : 'Sin opciones disponibles para este tipo de campo'
          }
        </div>

        <div className="flex justify-end mt-6">
          <button
            onClick={onClose}
            className="bg-gray-300 text-gray-700 px-4 py-2 rounded"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
};

export default TemplateEditor;