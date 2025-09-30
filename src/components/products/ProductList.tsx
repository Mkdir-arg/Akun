import React, { useState, useEffect } from 'react';
import { Search, Plus, Filter, Package, DollarSign } from 'lucide-react';
import ImportModal from './ImportModal';
import PriceListModal from './PriceListModal';

interface Product {
  id: number;
  sku: string;
  name: string;
  category_name: string;
  material: string;
  opening_type: string;
  glass_type: string;
  pricing_method: string;
  base_price: string;
  price_per_m2: string;
  is_active: boolean;
  is_service: boolean;
}

const ProductList: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter] = useState('');
  const [materialFilter, setMaterialFilter] = useState('');
  const [activeFilter, setActiveFilter] = useState('');
  const [showImportModal, setShowImportModal] = useState(false);
  const [showPriceModal, setShowPriceModal] = useState(false);

  useEffect(() => {
    fetchProducts();
  }, [searchTerm, categoryFilter, materialFilter, activeFilter]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchProducts = async () => {
    try {
      const params = new URLSearchParams();
      if (searchTerm) params.append('search', searchTerm);
      if (categoryFilter) params.append('category', categoryFilter);
      if (materialFilter) params.append('material', materialFilter);
      if (activeFilter) params.append('is_active', activeFilter);

      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/products/?${params}`, {
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        setProducts(data.results || data);
      }
    } catch (error) {
      console.error('Error fetching products:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (isActive: boolean) => {
    return isActive 
      ? 'bg-green-100 text-green-800' 
      : 'bg-gray-100 text-gray-800';
  };

  const getMaterialBadge = (material: string) => {
    const badges = {
      'ALUMINIO': 'bg-blue-100 text-blue-800',
      'PVC': 'bg-purple-100 text-purple-800',
      'MADERA': 'bg-orange-100 text-orange-800'
    };
    return badges[material as keyof typeof badges] || 'bg-gray-100 text-gray-800';
  };

  const formatPrice = (price: string, method: string) => {
    const numPrice = parseFloat(price);
    if (numPrice === 0) return '-';
    return method === 'FIXED' 
      ? `$${numPrice.toLocaleString()}` 
      : `$${numPrice.toLocaleString()}/m²`;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <>
      <header className="bg-white shadow-sm border-b px-4 lg:px-6 py-4">
        <div className="ml-12 lg:ml-0">
          <h2 className="text-xl lg:text-2xl font-bold text-gray-900">Productos</h2>
          <p className="text-sm lg:text-base text-gray-600">Gestión del catálogo de productos</p>
        </div>
      </header>
      
      <main className="flex-1 overflow-y-auto p-4 lg:p-6">
        <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4 mb-6">
          <div className="flex flex-col sm:flex-row gap-2">
            <button 
              onClick={() => setShowImportModal(true)}
              className="flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              <Package className="w-4 h-4 mr-2" />
              Importar
            </button>
            <button 
              onClick={() => setShowPriceModal(true)}
              className="flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              <DollarSign className="w-4 h-4 mr-2" />
              Precios
            </button>
            <button 
              onClick={() => window.location.hash = '/productos/nuevo'}
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700"
            >
              <Plus className="w-4 h-4 mr-2" />
              Nuevo Producto
            </button>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
          <div className="p-4">
            <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="Buscar productos..."
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              
              <select
                className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={materialFilter}
                onChange={(e) => setMaterialFilter(e.target.value)}
              >
                <option value="">Todos los materiales</option>
                <option value="ALUMINIO">Aluminio</option>
                <option value="PVC">PVC</option>
                <option value="MADERA">Madera</option>
              </select>

              <select
                className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={activeFilter}
                onChange={(e) => setActiveFilter(e.target.value)}
              >
                <option value="">Todos los estados</option>
                <option value="true">Activo</option>
                <option value="false">Inactivo</option>
              </select>

              <button className="flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
                <Filter className="w-4 h-4 mr-2" />
                Más filtros
              </button>
            </div>
          </div>
        </div>

        {/* Desktop Table */}
        <div className="hidden lg:block bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">SKU</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Producto</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Categoría</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Material</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tipo</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Precio</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {products.map((product) => (
                  <tr key={product.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900">{product.sku}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{product.name}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{product.category_name}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getMaterialBadge(product.material)}`}>
                        {product.material}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        product.is_service 
                          ? 'bg-indigo-100 text-indigo-800' 
                          : 'bg-green-100 text-green-800'
                      }`}>
                        {product.is_service ? 'Servicio' : 'Producto'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {product.pricing_method === 'FIXED' 
                        ? formatPrice(product.base_price, product.pricing_method)
                        : formatPrice(product.price_per_m2, product.pricing_method)
                      }
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusBadge(product.is_active)}`}>
                        {product.is_active ? 'Activo' : 'Inactivo'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex gap-2">
                        <button 
                          onClick={() => window.location.hash = `/productos/${product.id}`}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          Ver
                        </button>
                        <button 
                          onClick={() => window.location.hash = `/productos/${product.id}/editar`}
                          className="text-indigo-600 hover:text-indigo-900"
                        >
                          Editar
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Mobile Cards */}
        <div className="lg:hidden space-y-4">
          {products.map((product) => (
            <div key={product.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <h3 className="text-sm font-medium text-gray-900">{product.name}</h3>
                  <p className="text-xs text-gray-500 font-mono">{product.sku}</p>
                  <p className="text-xs text-gray-600 mt-1">{product.category_name}</p>
                </div>
                <div className="flex flex-col gap-1">
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getMaterialBadge(product.material)}`}>
                    {product.material}
                  </span>
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusBadge(product.is_active)}`}>
                    {product.is_active ? 'Activo' : 'Inactivo'}
                  </span>
                </div>
              </div>
              
              <div className="flex justify-between items-center mb-3">
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                  product.is_service 
                    ? 'bg-indigo-100 text-indigo-800' 
                    : 'bg-green-100 text-green-800'
                }`}>
                  {product.is_service ? 'Servicio' : 'Producto'}
                </span>
                <span className="text-sm font-medium text-gray-900">
                  {product.pricing_method === 'FIXED' 
                    ? formatPrice(product.base_price, product.pricing_method)
                    : formatPrice(product.price_per_m2, product.pricing_method)
                  }
                </span>
              </div>
              
              <div className="flex gap-2 pt-3 border-t border-gray-100">
                <button 
                  onClick={() => window.location.hash = `/productos/${product.id}`}
                  className="flex-1 px-3 py-2 text-xs font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100"
                >
                  Ver
                </button>
                <button 
                  onClick={() => window.location.hash = `/productos/${product.id}/editar`}
                  className="flex-1 px-3 py-2 text-xs font-medium text-indigo-600 bg-indigo-50 rounded-md hover:bg-indigo-100"
                >
                  Editar
                </button>
              </div>
            </div>
          ))}
        </div>

        {products.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">No se encontraron productos</p>
          </div>
        )}
        
        <ImportModal 
          isOpen={showImportModal} 
          onClose={() => setShowImportModal(false)} 
        />
        
        <PriceListModal 
          isOpen={showPriceModal} 
          onClose={() => setShowPriceModal(false)} 
        />
      </main>
    </>
  );
};

export default ProductList;