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
  attribute: Attribute;
  onAdd: (option: Omit<Option, 'id'>) => void;
  onUpdate: (id: number, updates: Partial<Option>) => void;
  onDelete: (id: number) => void;
}

const OptionTable: React.FC<Props> = ({ attribute, onAdd, onUpdate, onDelete }) => {
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [newOption, setNewOption] = useState({
    label: '',
    code: '',
    pricing_mode: 'ABS',
    price_value: '0',
    currency: 'ARS',
    order: attribute.options.length + 1,
    is_default: false
  });

  const handleAdd = () => {
    onAdd(newOption);
    setNewOption({
      label: '',
      code: '',
      pricing_mode: 'ABS',
      price_value: '0',
      currency: 'ARS',
      order: attribute.options.length + 2,
      is_default: false
    });
    setShowAddForm(false);
  };

  const handleEdit = (option: Option, field: string, value: any) => {
    if (option.id) {
      onUpdate(option.id, { [field]: value });
    }
  };

  const pricingModes = [
    { value: 'ABS', label: 'Absoluto' },
    { value: 'PER_M2', label: 'Por m²' },
    { value: 'PERIMETER', label: 'Por perímetro' },
    { value: 'FACTOR', label: 'Factor' }
  ];

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold">
          Opciones: {attribute.name}
        </h2>
        <button
          onClick={() => setShowAddForm(true)}
          className="bg-green-500 text-white px-3 py-1 rounded text-sm hover:bg-green-600"
        >
          + Opción
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b">
              <th className="text-left py-2">Orden</th>
              <th className="text-left py-2">Etiqueta</th>
              <th className="text-left py-2">Código</th>
              <th className="text-left py-2">Modo Precio</th>
              <th className="text-left py-2">Valor</th>
              <th className="text-left py-2">Default</th>
              <th className="text-left py-2">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {attribute.options.map((option) => (
              <tr key={option.id} className="border-b hover:bg-gray-50">
                <td className="py-2">
                  <input
                    type="number"
                    value={option.order}
                    onChange={(e) => handleEdit(option, 'order', parseInt(e.target.value))}
                    className="w-16 border rounded px-2 py-1"
                    min="1"
                  />
                </td>
                <td className="py-2">
                  {editingId === option.id ? (
                    <input
                      type="text"
                      value={option.label}
                      onChange={(e) => handleEdit(option, 'label', e.target.value)}
                      onBlur={() => setEditingId(null)}
                      onKeyDown={(e) => e.key === 'Enter' && setEditingId(null)}
                      className="border rounded px-2 py-1"
                      autoFocus
                    />
                  ) : (
                    <span
                      onDoubleClick={() => setEditingId(option.id || null)}
                      className="cursor-text"
                    >
                      {option.label}
                    </span>
                  )}
                </td>
                <td className="py-2">
                  <span className="text-gray-600 font-mono text-xs">
                    {option.code}
                  </span>
                </td>
                <td className="py-2">
                  <select
                    value={option.pricing_mode}
                    onChange={(e) => handleEdit(option, 'pricing_mode', e.target.value)}
                    className="border rounded px-2 py-1 text-xs"
                  >
                    {pricingModes.map(mode => (
                      <option key={mode.value} value={mode.value}>
                        {mode.label}
                      </option>
                    ))}
                  </select>
                </td>
                <td className="py-2">
                  <div className="flex items-center space-x-1">
                    <input
                      type="number"
                      step="0.01"
                      value={option.price_value}
                      onChange={(e) => handleEdit(option, 'price_value', e.target.value)}
                      className="w-20 border rounded px-2 py-1 text-xs"
                    />
                    <span className="text-xs text-gray-500">
                      {option.pricing_mode === 'ABS' && 'ARS'}
                      {option.pricing_mode === 'PER_M2' && '/m²'}
                      {option.pricing_mode === 'PERIMETER' && '/m'}
                      {option.pricing_mode === 'FACTOR' && 'x'}
                    </span>
                  </div>
                </td>
                <td className="py-2">
                  <input
                    type="checkbox"
                    checked={option.is_default}
                    onChange={(e) => handleEdit(option, 'is_default', e.target.checked)}
                  />
                </td>
                <td className="py-2">
                  <button
                    onClick={() => {
                      if (option.id) onDelete(option.id);
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

      {/* Formulario para agregar opción */}
      {showAddForm && (
        <div className="mt-4 p-4 border rounded bg-gray-50">
          <h3 className="font-medium mb-3">Nueva Opción</h3>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium mb-1">Etiqueta</label>
              <input
                type="text"
                value={newOption.label}
                onChange={(e) => setNewOption(prev => ({ ...prev, label: e.target.value }))}
                className="w-full border rounded px-2 py-1 text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium mb-1">Código</label>
              <input
                type="text"
                value={newOption.code}
                onChange={(e) => setNewOption(prev => ({ ...prev, code: e.target.value }))}
                className="w-full border rounded px-2 py-1 text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium mb-1">Modo de Precio</label>
              <select
                value={newOption.pricing_mode}
                onChange={(e) => setNewOption(prev => ({ ...prev, pricing_mode: e.target.value }))}
                className="w-full border rounded px-2 py-1 text-sm"
              >
                {pricingModes.map(mode => (
                  <option key={mode.value} value={mode.value}>
                    {mode.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium mb-1">Valor</label>
              <input
                type="number"
                step="0.01"
                value={newOption.price_value}
                onChange={(e) => setNewOption(prev => ({ ...prev, price_value: e.target.value }))}
                className="w-full border rounded px-2 py-1 text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium mb-1">Orden</label>
              <input
                type="number"
                value={newOption.order}
                onChange={(e) => setNewOption(prev => ({ ...prev, order: parseInt(e.target.value) }))}
                className="w-full border rounded px-2 py-1 text-sm"
                min="1"
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
              <span className="text-sm">Opción por defecto</span>
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

      {attribute.options.length === 0 && !showAddForm && (
        <div className="text-center py-8 text-gray-500">
          No hay opciones definidas. Haga clic en "+ Opción" para agregar una.
        </div>
      )}
    </div>
  );
};

export default OptionTable;