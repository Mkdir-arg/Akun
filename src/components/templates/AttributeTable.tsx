import React, { useState } from 'react';

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

interface Props {
  attributes: Attribute[];
  onAdd: (attribute: Omit<Attribute, 'id' | 'options'>) => void;
  onUpdate: (id: number, updates: Partial<Attribute>) => void;
  onDelete: (id: number) => void;
  onSelect: (attribute: Attribute | null) => void;
  selectedAttribute: Attribute | null;
}

const AttributeTable: React.FC<Props> = ({
  attributes,
  onAdd,
  onUpdate,
  onDelete,
  onSelect,
  selectedAttribute
}) => {
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [newAttribute, setNewAttribute] = useState({
    name: '',
    code: '',
    type: 'SELECT',
    is_required: true,
    order: attributes.length + 1,
    rules_json: {}
  });

  const handleAdd = () => {
    onAdd(newAttribute);
    setNewAttribute({
      name: '',
      code: '',
      type: 'SELECT',
      is_required: true,
      order: attributes.length + 2,
      rules_json: {}
    });
    setShowAddForm(false);
  };

  const handleEdit = (attribute: Attribute, field: string, value: any) => {
    if (attribute.id) {
      onUpdate(attribute.id, { [field]: value });
    }
  };

  const attributeTypes = [
    { value: 'SELECT', label: 'Select' },
    { value: 'BOOLEAN', label: 'Boolean' },
    { value: 'NUMBER', label: 'Number' },
    { value: 'COLOR', label: 'Color' },
    { value: 'MEASURE_MM', label: 'Measure (mm)' }
  ];

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold">Atributos</h2>
        <button
          onClick={() => setShowAddForm(true)}
          className="bg-green-500 text-white px-3 py-1 rounded text-sm hover:bg-green-600"
        >
          + Atributo
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b">
              <th className="text-left py-2">Orden</th>
              <th className="text-left py-2">Nombre</th>
              <th className="text-left py-2">Código</th>
              <th className="text-left py-2">Tipo</th>
              <th className="text-left py-2">Obligatorio</th>
              <th className="text-left py-2">Opciones</th>
              <th className="text-left py-2">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {attributes.map((attribute) => (
              <tr
                key={attribute.id}
                className={`border-b hover:bg-gray-50 cursor-pointer ${
                  selectedAttribute?.id === attribute.id ? 'bg-blue-50' : ''
                }`}
                onClick={() => onSelect(attribute)}
              >
                <td className="py-2">
                  <input
                    type="number"
                    value={attribute.order}
                    onChange={(e) => handleEdit(attribute, 'order', parseInt(e.target.value))}
                    className="w-16 border rounded px-2 py-1"
                    min="1"
                  />
                </td>
                <td className="py-2">
                  {editingId === attribute.id ? (
                    <input
                      type="text"
                      value={attribute.name}
                      onChange={(e) => handleEdit(attribute, 'name', e.target.value)}
                      onBlur={() => setEditingId(null)}
                      onKeyDown={(e) => e.key === 'Enter' && setEditingId(null)}
                      className="border rounded px-2 py-1"
                      autoFocus
                    />
                  ) : (
                    <span
                      onDoubleClick={() => setEditingId(attribute.id || null)}
                      className="cursor-text"
                    >
                      {attribute.name}
                    </span>
                  )}
                </td>
                <td className="py-2">
                  <span className="text-gray-600 font-mono text-xs">
                    {attribute.code}
                  </span>
                </td>
                <td className="py-2">
                  <select
                    value={attribute.type}
                    onChange={(e) => handleEdit(attribute, 'type', e.target.value)}
                    className="border rounded px-2 py-1 text-xs"
                  >
                    {attributeTypes.map(type => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </select>
                </td>
                <td className="py-2">
                  <input
                    type="checkbox"
                    checked={attribute.is_required}
                    onChange={(e) => handleEdit(attribute, 'is_required', e.target.checked)}
                  />
                </td>
                <td className="py-2">
                  <span className="text-sm text-gray-600">
                    {attribute.options?.length || 0}
                  </span>
                </td>
                <td className="py-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      if (attribute.id) onDelete(attribute.id);
                    }}
                    className="text-red-600 hover:text-red-800 text-xs"
                  >
                    Eliminar
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Formulario para agregar atributo */}
      {showAddForm && (
        <div className="mt-4 p-4 border rounded bg-gray-50">
          <h3 className="font-medium mb-3">Nuevo Atributo</h3>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium mb-1">Nombre</label>
              <input
                type="text"
                value={newAttribute.name}
                onChange={(e) => setNewAttribute(prev => ({ ...prev, name: e.target.value }))}
                className="w-full border rounded px-2 py-1 text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium mb-1">Código</label>
              <input
                type="text"
                value={newAttribute.code}
                onChange={(e) => setNewAttribute(prev => ({ ...prev, code: e.target.value }))}
                className="w-full border rounded px-2 py-1 text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium mb-1">Tipo</label>
              <select
                value={newAttribute.type}
                onChange={(e) => setNewAttribute(prev => ({ ...prev, type: e.target.value }))}
                className="w-full border rounded px-2 py-1 text-sm"
              >
                {attributeTypes.map(type => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium mb-1">Orden</label>
              <input
                type="number"
                value={newAttribute.order}
                onChange={(e) => setNewAttribute(prev => ({ ...prev, order: parseInt(e.target.value) }))}
                className="w-full border rounded px-2 py-1 text-sm"
                min="1"
              />
            </div>
          </div>
          <div className="mt-3">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={newAttribute.is_required}
                onChange={(e) => setNewAttribute(prev => ({ ...prev, is_required: e.target.checked }))}
              />
              <span className="text-sm">Obligatorio</span>
            </label>
          </div>
          <div className="mt-3 space-x-2">
            <button
              onClick={handleAdd}
              className="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600"
            >
              Agregar
            </button>
            <button
              onClick={() => setShowAddForm(false)}
              className="border border-gray-300 px-3 py-1 rounded text-sm hover:bg-gray-50"
            >
              Cancelar
            </button>
          </div>
        </div>
      )}

      {attributes.length === 0 && !showAddForm && (
        <div className="text-center py-8 text-gray-500">
          No hay atributos definidos. Haga clic en "+ Atributo" para agregar uno.
        </div>
      )}
    </div>
  );
};

export default AttributeTable;