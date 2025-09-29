import React, { useState, useEffect } from 'react';
import { Plus, Edit, Trash2 } from 'lucide-react';

interface Category {
  id: number;
  name: string;
  code: string;
  parent: number | null;
  parent_name?: string;
  is_active: boolean;
  subcategories: Subcategory[];
}

interface Subcategory {
  id: number;
  category: number;
  category_name: string;
  name: string;
  code: string;
  description: string;
  is_active: boolean;
}

const CategoryList: React.FC = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [subcategories, setSubcategories] = useState<Subcategory[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCategoryForm, setShowCategoryForm] = useState(false);
  const [showSubcategoryForm, setShowSubcategoryForm] = useState(false);
  const [editingCategory, setEditingCategory] = useState<Category | null>(null);
  const [editingSubcategory, setEditingSubcategory] = useState<Subcategory | null>(null);

  const [categoryForm, setCategoryForm] = useState({
    name: '',
    code: '',
    parent: '',
    is_active: true
  });

  const [subcategoryForm, setSubcategoryForm] = useState({
    category: '',
    name: '',
    code: '',
    description: '',
    is_active: true
  });

  useEffect(() => {
    fetchCategories();
    fetchSubcategories();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/categories/`, {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setCategories(data.results || data);
      }
    } catch (error) {
      console.error('Error fetching categories:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSubcategories = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/subcategories/`, {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setSubcategories(data.results || data);
      }
    } catch (error) {
      console.error('Error fetching subcategories:', error);
    }
  };

  const handleCategorySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const url = editingCategory 
      ? `${process.env.REACT_APP_API_URL}/api/categories/${editingCategory.id}/`
      : `${process.env.REACT_APP_API_URL}/api/categories/`;
    
    const method = editingCategory ? 'PUT' : 'POST';
    
    try {
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          ...categoryForm,
          parent: categoryForm.parent || null
        })
      });

      if (response.ok) {
        fetchCategories();
        setShowCategoryForm(false);
        setEditingCategory(null);
        setCategoryForm({ name: '', code: '', parent: '', is_active: true });
      }
    } catch (error) {
      console.error('Error saving category:', error);
    }
  };

  const handleSubcategorySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const url = editingSubcategory 
      ? `${process.env.REACT_APP_API_URL}/api/subcategories/${editingSubcategory.id}/`
      : `${process.env.REACT_APP_API_URL}/api/subcategories/`;
    
    const method = editingSubcategory ? 'PUT' : 'POST';
    
    try {
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(subcategoryForm)
      });

      if (response.ok) {
        fetchSubcategories();
        setShowSubcategoryForm(false);
        setEditingSubcategory(null);
        setSubcategoryForm({ category: '', name: '', code: '', description: '', is_active: true });
      }
    } catch (error) {
      console.error('Error saving subcategory:', error);
    }
  };

  const handleEditCategory = (category: Category) => {
    setEditingCategory(category);
    setCategoryForm({
      name: category.name,
      code: category.code,
      parent: category.parent?.toString() || '',
      is_active: category.is_active
    });
    setShowCategoryForm(true);
  };

  const handleEditSubcategory = (subcategory: Subcategory) => {
    setEditingSubcategory(subcategory);
    setSubcategoryForm({
      category: subcategory.category.toString(),
      name: subcategory.name,
      code: subcategory.code,
      description: subcategory.description,
      is_active: subcategory.is_active
    });
    setShowSubcategoryForm(true);
  };

  const handleDeleteCategory = async (id: number) => {
    if (window.confirm('¿Estás seguro de eliminar esta categoría?')) {
      try {
        const response = await fetch(`${process.env.REACT_APP_API_URL}/api/categories/${id}/`, {
          method: 'DELETE',
          credentials: 'include'
        });
        if (response.ok) {
          fetchCategories();
        }
      } catch (error) {
        console.error('Error deleting category:', error);
      }
    }
  };

  const handleDeleteSubcategory = async (id: number) => {
    if (window.confirm('¿Estás seguro de eliminar esta subcategoría?')) {
      try {
        const response = await fetch(`${process.env.REACT_APP_API_URL}/api/subcategories/${id}/`, {
          method: 'DELETE',
          credentials: 'include'
        });
        if (response.ok) {
          fetchSubcategories();
        }
      } catch (error) {
        console.error('Error deleting subcategory:', error);
      }
    }
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
      <header className="bg-white shadow-sm border-b px-6 py-4">
        <h2 className="text-2xl font-bold text-gray-900">Categorías y Subcategorías</h2>
        <p className="text-gray-600">Gestión de categorías de productos</p>
      </header>

      <main className="flex-1 overflow-y-auto p-6">
        <div className="flex justify-between items-center mb-6">
          <div className="flex gap-2">
            <button 
              onClick={() => setShowCategoryForm(true)}
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              <Plus className="w-4 h-4 mr-2" />
              Nueva Categoría
            </button>
            <button 
              onClick={() => setShowSubcategoryForm(true)}
              className="flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
            >
              <Plus className="w-4 h-4 mr-2" />
              Nueva Subcategoría
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Categorías */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-4 border-b">
              <h3 className="text-lg font-semibold">Categorías</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nombre</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Código</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Acciones</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {categories.map((category) => (
                    <tr key={category.id}>
                      <td className="px-4 py-3 text-sm text-gray-900">{category.name}</td>
                      <td className="px-4 py-3 text-sm text-gray-500">{category.code}</td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          category.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {category.is_active ? 'Activo' : 'Inactivo'}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <button 
                          onClick={() => handleEditCategory(category)}
                          className="text-blue-600 hover:text-blue-900 mr-2"
                        >
                          <Edit className="w-4 h-4" />
                        </button>
                        <button 
                          onClick={() => handleDeleteCategory(category.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Subcategorías */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-4 border-b">
              <h3 className="text-lg font-semibold">Subcategorías</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Categoría</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nombre</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Acciones</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {subcategories.map((subcategory) => (
                    <tr key={subcategory.id}>
                      <td className="px-4 py-3 text-sm text-gray-500">{subcategory.category_name}</td>
                      <td className="px-4 py-3 text-sm text-gray-900">{subcategory.name}</td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          subcategory.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {subcategory.is_active ? 'Activo' : 'Inactivo'}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <button 
                          onClick={() => handleEditSubcategory(subcategory)}
                          className="text-blue-600 hover:text-blue-900 mr-2"
                        >
                          <Edit className="w-4 h-4" />
                        </button>
                        <button 
                          onClick={() => handleDeleteSubcategory(subcategory.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </main>

      {/* Modal Categoría */}
      {showCategoryForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">
              {editingCategory ? 'Editar Categoría' : 'Nueva Categoría'}
            </h3>
            <form onSubmit={handleCategorySubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Nombre</label>
                <input
                  type="text"
                  value={categoryForm.name}
                  onChange={(e) => setCategoryForm({...categoryForm, name: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Código</label>
                <input
                  type="text"
                  value={categoryForm.code}
                  onChange={(e) => setCategoryForm({...categoryForm, code: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  checked={categoryForm.is_active}
                  onChange={(e) => setCategoryForm({...categoryForm, is_active: e.target.checked})}
                  className="mr-2"
                />
                <label className="text-sm text-gray-700">Activo</label>
              </div>
              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowCategoryForm(false);
                    setEditingCategory(null);
                    setCategoryForm({ name: '', code: '', parent: '', is_active: true });
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  {editingCategory ? 'Actualizar' : 'Crear'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal Subcategoría */}
      {showSubcategoryForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">
              {editingSubcategory ? 'Editar Subcategoría' : 'Nueva Subcategoría'}
            </h3>
            <form onSubmit={handleSubcategorySubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Categoría</label>
                <select
                  value={subcategoryForm.category}
                  onChange={(e) => setSubcategoryForm({...subcategoryForm, category: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="">Seleccionar categoría</option>
                  {categories.map((cat) => (
                    <option key={cat.id} value={cat.id}>{cat.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Nombre</label>
                <input
                  type="text"
                  value={subcategoryForm.name}
                  onChange={(e) => setSubcategoryForm({...subcategoryForm, name: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Código</label>
                <input
                  type="text"
                  value={subcategoryForm.code}
                  onChange={(e) => setSubcategoryForm({...subcategoryForm, code: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Descripción</label>
                <textarea
                  value={subcategoryForm.description}
                  onChange={(e) => setSubcategoryForm({...subcategoryForm, description: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={3}
                />
              </div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  checked={subcategoryForm.is_active}
                  onChange={(e) => setSubcategoryForm({...subcategoryForm, is_active: e.target.checked})}
                  className="mr-2"
                />
                <label className="text-sm text-gray-700">Activo</label>
              </div>
              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowSubcategoryForm(false);
                    setEditingSubcategory(null);
                    setSubcategoryForm({ category: '', name: '', code: '', description: '', is_active: true });
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                >
                  {editingSubcategory ? 'Actualizar' : 'Crear'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
};

export default CategoryList;