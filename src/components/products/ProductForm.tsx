import React, { useState, useEffect } from 'react';
import { ArrowLeft, Save } from 'lucide-react';

interface ProductFormProps {
  productId?: string;
  onBack: () => void;
  onSave: () => void;
}

interface Category {
  id: number;
  name: string;
}

interface UoM {
  id: number;
  name: string;
  code: string;
}

interface TaxRate {
  id: number;
  name: string;
  rate: string;
}

const ProductForm: React.FC<ProductFormProps> = ({ productId, onBack, onSave }) => {
  const [formData, setFormData] = useState({
    sku: '',
    name: '',
    category: '',
    uom: '',
    material: 'ALUMINIO',
    opening_type: 'CORREDIZA',
    glass_type: 'DVH',
    color_code: '',
    width_mm: '',
    height_mm: '',
    weight_kg: '',
    tax: '',
    pricing_method: 'FIXED',
    base_price: '0',
    price_per_m2: '0',
    min_area_m2: '1.00',
    is_service: false,
    is_active: true
  });

  const [categories, setCategories] = useState<Category[]>([]);
  const [uoms, setUoms] = useState<UoM[]>([]);
  const [taxRates, setTaxRates] = useState<TaxRate[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchFormData();
    if (productId) {
      fetchProduct();
    } else {
      setLoading(false);
    }
  }, [productId]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchFormData = async () => {
    try {
      const [categoriesRes, uomsRes, taxRatesRes] = await Promise.all([
        fetch(`${process.env.REACT_APP_API_URL}/api/categories/`, { credentials: 'include' }),
        fetch(`${process.env.REACT_APP_API_URL}/api/uoms/`, { credentials: 'include' }),
        fetch(`${process.env.REACT_APP_API_URL}/api/tax-rates/`, { credentials: 'include' })
      ]);

      if (categoriesRes.ok) {
        const categoriesData = await categoriesRes.json();
        setCategories(categoriesData.results || categoriesData);
      }

      if (uomsRes.ok) {
        const uomsData = await uomsRes.json();
        setUoms(uomsData.results || uomsData);
      }

      if (taxRatesRes.ok) {
        const taxRatesData = await taxRatesRes.json();
        setTaxRates(taxRatesData.results || taxRatesData);
        
        // Seleccionar tasa por defecto
        const defaultTax = (taxRatesData.results || taxRatesData).find((tax: TaxRate) => tax.name.includes('21%'));
        if (defaultTax && !productId) {
          setFormData(prev => ({ ...prev, tax: defaultTax.id.toString() }));
        }
      }
    } catch (error) {
      console.error('Error fetching form data:', error);
    }
  };

  const fetchProduct = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/products/${productId}/`, {
        credentials: 'include'
      });
      if (response.ok) {
        const product = await response.json();
        setFormData({
          sku: product.sku,
          name: product.name,
          category: product.category.toString(),
          uom: product.uom.toString(),
          material: product.material,
          opening_type: product.opening_type,
          glass_type: product.glass_type || '',
          color_code: product.color_code || '',
          width_mm: product.width_mm?.toString() || '',
          height_mm: product.height_mm?.toString() || '',
          weight_kg: product.weight_kg?.toString() || '',
          tax: product.tax.toString(),
          pricing_method: product.pricing_method,
          base_price: product.base_price,
          price_per_m2: product.price_per_m2,
          min_area_m2: product.min_area_m2,
          is_service: product.is_service,
          is_active: product.is_active
        });
      }
    } catch (error) {
      console.error('Error fetching product:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const submitData = {
        ...formData,
        category: parseInt(formData.category),
        uom: parseInt(formData.uom),
        tax: parseInt(formData.tax),
        width_mm: formData.width_mm ? parseInt(formData.width_mm) : null,
        height_mm: formData.height_mm ? parseInt(formData.height_mm) : null,
        weight_kg: formData.weight_kg ? parseFloat(formData.weight_kg) : null,
        base_price: parseFloat(formData.base_price),
        price_per_m2: parseFloat(formData.price_per_m2),
        min_area_m2: parseFloat(formData.min_area_m2)
      };

      const url = productId 
        ? `${process.env.REACT_APP_API_URL}/api/products/${productId}/`
        : `${process.env.REACT_APP_API_URL}/api/products/`;
      
      const method = productId ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(submitData)
      });

      if (response.ok) {
        onSave();
      }
    } catch (error) {
      console.error('Error saving product:', error);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <>
      <header className="bg-white shadow-sm border-b px-6 py-4">
        <div className="flex items-center">
          <button onClick={onBack} className="mr-4 p-2 hover:bg-gray-100 rounded-lg">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              {productId ? 'Editar Producto' : 'Nuevo Producto'}
            </h2>
            <p className="text-gray-600">
              {productId ? 'Modificar información del producto' : 'Crear un nuevo producto'}
            </p>
          </div>
        </div>
      </header>

      <main className="flex-1 overflow-y-auto p-6">
        <div className="max-w-4xl mx-auto">
          <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  SKU *
                </label>
                <input
                  type="text"
                  name="sku"
                  value={formData.sku}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Categoría *
                </label>
                <select
                  name="category"
                  value={formData.category}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="">Seleccionar categoría</option>
                  {categories.map((category) => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nombre del Producto *
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Unidad de Medida *
                </label>
                <select
                  name="uom"
                  value={formData.uom}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="">Seleccionar UoM</option>
                  {uoms.map((uom) => (
                    <option key={uom.id} value={uom.id}>
                      {uom.name} ({uom.code})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Material *
                </label>
                <select
                  name="material"
                  value={formData.material}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="ALUMINIO">Aluminio</option>
                  <option value="PVC">PVC</option>
                  <option value="MADERA">Madera</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tipo de Apertura *
                </label>
                <select
                  name="opening_type"
                  value={formData.opening_type}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="CORREDIZA">Corrediza</option>
                  <option value="BATIENTE">Batiente</option>
                  <option value="OSCILOBATIENTE">Oscilobatiente</option>
                  <option value="PAÑO_FIJO">Paño Fijo</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tipo de Vidrio
                </label>
                <select
                  name="glass_type"
                  value={formData.glass_type}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Sin vidrio</option>
                  <option value="SIMPLE">Simple</option>
                  <option value="DVH">DVH</option>
                  <option value="LAMINADO">Laminado</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Método de Precio *
                </label>
                <select
                  name="pricing_method"
                  value={formData.pricing_method}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="FIXED">Precio Fijo</option>
                  <option value="AREA">Por Área</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Impuesto *
                </label>
                <select
                  name="tax"
                  value={formData.tax}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="">Seleccionar impuesto</option>
                  {taxRates.map((tax) => (
                    <option key={tax.id} value={tax.id}>
                      {tax.name} ({tax.rate}%)
                    </option>
                  ))}
                </select>
              </div>

              {formData.pricing_method === 'FIXED' ? (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Precio Base
                  </label>
                  <input
                    type="number"
                    name="base_price"
                    value={formData.base_price}
                    onChange={handleChange}
                    min="0"
                    step="0.01"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              ) : (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Precio por m²
                    </label>
                    <input
                      type="number"
                      name="price_per_m2"
                      value={formData.price_per_m2}
                      onChange={handleChange}
                      min="0"
                      step="0.01"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Área Mínima (m²)
                    </label>
                    <input
                      type="number"
                      name="min_area_m2"
                      value={formData.min_area_m2}
                      onChange={handleChange}
                      min="0"
                      step="0.01"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </>
              )}

              <div className="md:col-span-2">
                <div className="flex items-center space-x-6">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      name="is_service"
                      checked={formData.is_service}
                      onChange={handleChange}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="ml-2 text-sm text-gray-700">Es un servicio</span>
                  </label>
                  
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      name="is_active"
                      checked={formData.is_active}
                      onChange={handleChange}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="ml-2 text-sm text-gray-700">Activo</span>
                  </label>
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <button
                type="button"
                onClick={onBack}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              >
                Cancelar
              </button>
              <button
                type="submit"
                className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                <Save className="w-4 h-4 mr-2" />
                Guardar
              </button>
            </div>
          </form>
        </div>
      </main>
    </>
  );
};

export default ProductForm;