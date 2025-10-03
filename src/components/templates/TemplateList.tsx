import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Plus, Edit, Copy, Trash2, Eye, Search, Filter } from 'lucide-react';

interface TemplateCategorySummary {
  id: number;
  legacy_extrusora_id: number;
  legacy_extrusora_name?: string;
  name: string;
  slug: string;
  description: string;
  templates: number;
  active_templates: number;
  product_classes: Record<string, number>;
  lines: Record<string, number>;
}

interface ProductTemplate {
  id: number;
  product_class: string;
  line_name: string;
  code: string;
  version: number;
  is_active: boolean;
  created_at: string | null;
  attributes_count?: number;
  category_id?: number | null;
  legacy_extrusora_id?: number | null;
  requires_dimensions?: boolean;
  base_price_net?: number;
}

interface AssociatedProduct {
  id: number;
  product_class: string;
  line_name: string;
  code: string;
  base_price_net: number;
  currency: string;
  relationship_type: string;
}

interface AssociatedResponse {
  main_product: {
    id: number;
    product_class: string;
    line_name: string;
    code: string;
  };
  associated_products: AssociatedProduct[];
}

interface TemplateListProps {
  onEdit?: (templateId: number) => void;
  onPreview?: (templateId: number) => void;
}

const ITEMS_PER_PAGE = 12;

export const TemplateList: React.FC<TemplateListProps> = ({ onEdit, onPreview }) => {
  const [categories, setCategories] = useState<TemplateCategorySummary[]>([]);
  const [loadingCategories, setLoadingCategories] = useState(true);
  const [categoryError, setCategoryError] = useState<string | null>(null);

  const [selectedCategoryId, setSelectedCategoryId] = useState<number | null>(null);
  const [selectedCategoryName, setSelectedCategoryName] = useState('');

  const [templates, setTemplates] = useState<ProductTemplate[]>([]);
  const [loadingTemplates, setLoadingTemplates] = useState(false);
  const [templatesError, setTemplatesError] = useState<string | null>(null);

  const [selectedProductClass, setSelectedProductClass] = useState<string | null>(null);
  const [selectedLine, setSelectedLine] = useState<string | null>(null);
  const [selectedTemplate, setSelectedTemplate] = useState<ProductTemplate | null>(null);

  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  const [associatedData, setAssociatedData] = useState<AssociatedResponse | null>(null);
  const [associatedLoading, setAssociatedLoading] = useState(false);
  const [associatedError, setAssociatedError] = useState<string | null>(null);

  const [currentPage, setCurrentPage] = useState(1);
  const [showNewTemplateForm, setShowNewTemplateForm] = useState(false);
  const [newTemplateName, setNewTemplateName] = useState('');

  const selectedCategory = useMemo(
    () => categories.find((category) => category.id === selectedCategoryId) || null,
    [categories, selectedCategoryId],
  );

  const groupedByClass = useMemo(() => {
    return templates.reduce<Record<string, ProductTemplate[]>>((acc, template) => {
      if (!acc[template.product_class]) {
        acc[template.product_class] = [];
      }
      acc[template.product_class].push(template);
      return acc;
    }, {});
  }, [templates]);

  const lineGroups = useMemo(() => {
    if (!selectedProductClass) {
      return {} as Record<string, ProductTemplate[]>;
    }
    const classTemplates = groupedByClass[selectedProductClass] || [];
    return classTemplates.reduce<Record<string, ProductTemplate[]>>((acc, template) => {
      if (!acc[template.line_name]) {
        acc[template.line_name] = [];
      }
      acc[template.line_name].push(template);
      return acc;
    }, {});
  }, [groupedByClass, selectedProductClass]);

  const filteredTemplates = useMemo(() => {
    return templates.filter((template) => {
      if (selectedProductClass && template.product_class !== selectedProductClass) {
        return false;
      }
      if (selectedLine && template.line_name !== selectedLine) {
        return false;
      }
      if (statusFilter) {
        const shouldBeActive = statusFilter === 'true';
        if (template.is_active !== shouldBeActive) {
          return false;
        }
      }
      if (searchTerm && !template.line_name.toLowerCase().includes(searchTerm.toLowerCase())) {
        return false;
      }
      return true;
    });
  }, [templates, selectedProductClass, selectedLine, statusFilter, searchTerm]);
  const fetchCategories = useCallback(async () => {
    try {
      setCategoryError(null);
      setLoadingCategories(true);
      const response = await fetch('/api/template-categories/');
      if (!response.ok) {
        throw new Error('No fue posible obtener las extrusoras.');
      }
      const data = await response.json();
      setCategories(data.categories || []);
    } catch (error) {
      console.error('Error fetching categories:', error);
      setCategoryError('No se pudieron cargar las extrusoras.');
      setCategories([]);
    } finally {
      setLoadingCategories(false);
    }
  }, []);

  const fetchTemplates = useCallback(async () => {
    if (selectedCategoryId === null) {
      setTemplates([]);
      setTemplatesError(null);
      return;
    }

    try {
      setTemplatesError(null);
      setLoadingTemplates(true);
      const params = new URLSearchParams();
      params.append('category_id', String(selectedCategoryId));
      if (selectedCategory?.legacy_extrusora_id !== undefined) {
        params.append('extrusora_id', String(selectedCategory.legacy_extrusora_id));
      }
      if (statusFilter) {
        params.append('active', statusFilter);
      }
      if (searchTerm) {
        params.append('line_name', searchTerm);
      }

      const response = await fetch(`/api/templates/?${params.toString()}`);
      if (!response.ok) {
        throw new Error('No fue posible obtener las plantillas.');
      }
      const data = await response.json();
      const templateList: ProductTemplate[] = data.templates || data.results || data || [];
      setTemplates(templateList);

      if (selectedProductClass && !templateList.some((tpl) => tpl.product_class === selectedProductClass)) {
        setSelectedProductClass(null);
        setSelectedLine(null);
        setSelectedTemplate(null);
        setAssociatedData(null);
      }
      if (selectedLine && !templateList.some((tpl) => tpl.line_name === selectedLine)) {
        setSelectedLine(null);
        setSelectedTemplate(null);
        setAssociatedData(null);
      }
      if (selectedTemplate && !templateList.some((tpl) => tpl.id === selectedTemplate.id)) {
        setSelectedTemplate(null);
        setAssociatedData(null);
      }
    } catch (error) {
      console.error('Error fetching templates:', error);
      setTemplatesError('No se pudieron cargar las plantillas.');
      setTemplates([]);
    } finally {
      setLoadingTemplates(false);
    }
  }, [searchTerm, selectedCategory, selectedCategoryId, selectedLine, selectedProductClass, selectedTemplate, statusFilter]);

  useEffect(() => {
    fetchCategories();
  }, [fetchCategories]);

  useEffect(() => {
    setCurrentPage(1);
  }, [categories.length]);

  useEffect(() => {
    if (selectedCategoryId !== null && !categories.some((category) => category.id === selectedCategoryId)) {
      setSelectedCategoryId(null);
      setSelectedCategoryName('');
      setSelectedProductClass(null);
      setSelectedLine(null);
      setSelectedTemplate(null);
      setAssociatedData(null);
    }
  }, [categories, selectedCategoryId]);

  useEffect(() => {
    if (selectedCategoryId === null) {
      setTemplates([]);
      setSelectedProductClass(null);
      setSelectedLine(null);
      setSelectedTemplate(null);
      setAssociatedData(null);
      setAssociatedError(null);
      return;
    }
    fetchTemplates();
  }, [fetchTemplates, selectedCategoryId]);

  useEffect(() => {
    if (selectedProductClass && !(groupedByClass[selectedProductClass] || []).length) {
      setSelectedProductClass(null);
      setSelectedLine(null);
      setSelectedTemplate(null);
      setAssociatedData(null);
    }
  }, [groupedByClass, selectedProductClass]);

  useEffect(() => {
    if (selectedLine && !(lineGroups[selectedLine] || []).length) {
      setSelectedLine(null);
      setSelectedTemplate(null);
      setAssociatedData(null);
    }
  }, [lineGroups, selectedLine]);
  const loadAssociated = useCallback(async (template: ProductTemplate) => {
    try {
      setAssociatedLoading(true);
      setAssociatedError(null);
      const response = await fetch(`/api/templates/${template.id}/associated/`);
      if (!response.ok) {
        throw new Error('No fue posible obtener los accesorios relacionados.');
      }
      const data: AssociatedResponse = await response.json();
      setAssociatedData(data);
    } catch (error) {
      console.error('Error fetching associated products:', error);
      setAssociatedData(null);
      setAssociatedError('No se pudieron obtener los accesorios relacionados.');
    } finally {
      setAssociatedLoading(false);
    }
  }, []);

  const handleSelectTemplate = useCallback(
    (template: ProductTemplate) => {
      setSelectedTemplate(template);
      loadAssociated(template);
    },
    [loadAssociated],
  );

  const handleClone = useCallback(
    async (templateId: number) => {
      try {
        const response = await fetch(`/api/templates/${templateId}/clone/`, {
          method: 'POST',
        });
        if (response.ok) {
          fetchTemplates();
        }
      } catch (error) {
        console.error('Error cloning template:', error);
      }
    },
    [fetchTemplates],
  );

  const handleDelete = useCallback(
    async (templateId: number) => {
      if (!window.confirm('¿Estás seguro de eliminar esta plantilla?')) {
        return;
      }
      try {
        const response = await fetch(`/api/templates/${templateId}/`, {
          method: 'DELETE',
        });
        if (response.ok) {
          fetchTemplates();
        }
      } catch (error) {
        console.error('Error deleting template:', error);
      }
    },
    [fetchTemplates],
  );

  const handleCreateTemplate = useCallback(async () => {
    if (!selectedCategoryId) {
      alert('Selecciona una extrusora antes de crear una plantilla.');
      return;
    }
    if (!newTemplateName.trim()) {
      alert('Ingresa un nombre para la nueva plantilla.');
      return;
    }

    try {
      const response = await fetch('/api/templates/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          line_name: newTemplateName,
          code: newTemplateName.toLowerCase().replace(/\s+/g, '-'),
          product_class: selectedProductClass || 'VENTANA',
          base_price_net: 0,
          currency: 'ARS',
          requires_dimensions: true,
          is_active: true,
          version: 1,
          category_id: selectedCategoryId,
          legacy_extrusora_id: selectedCategory?.legacy_extrusora_id ?? null,
        }),
      });
      if (!response.ok) {
        throw new Error('No se pudo crear la plantilla.');
      }
      setShowNewTemplateForm(false);
      setNewTemplateName('');
      fetchTemplates();
    } catch (error) {
      console.error('Error creating template:', error);
      alert('Error al crear la plantilla.');
    }
  }, [fetchTemplates, newTemplateName, selectedCategory, selectedCategoryId, selectedProductClass]);
  const getStatusBadge = (isActive: boolean) => (
    <span
      className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
        isActive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
      }`}
    >
      {isActive ? 'Activo' : 'Inactivo'}
    </span>
  );

  const getClassBadge = (productClass: string) => {
    const colors: Record<string, string> = {
      VENTANA: 'bg-blue-100 text-blue-800',
      PUERTA: 'bg-green-100 text-green-800',
      ACCESORIO: 'bg-purple-100 text-purple-800',
    };

    return (
      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${colors[productClass] || 'bg-gray-100 text-gray-800'}`}>
        {productClass}
      </span>
    );
  };
  const renderCategoryRows = () => {
    if (categoryError) {
      return (
        <tr>
          <td colSpan={7} className="px-6 py-6 text-center text-sm text-red-600">
            {categoryError}
          </td>
        </tr>
      );
    }

    if (!categories.length) {
      return (
        <tr>
          <td colSpan={7} className="px-6 py-6 text-center text-sm text-gray-500">
            No hay extrusoras cargadas. Ejecutá la sincronización para importar datos legacy.
          </td>
        </tr>
      );
    }

    const pageItems = categories.slice((currentPage - 1) * ITEMS_PER_PAGE, currentPage * ITEMS_PER_PAGE);

    return pageItems.map((category) => (
      <tr
        key={category.id}
        className="hover:bg-gray-50 cursor-pointer"
        onClick={() => {
          setSelectedCategoryId(category.id);
          setSelectedCategoryName(category.legacy_extrusora_name || category.name);
          setSelectedProductClass(null);
          setSelectedLine(null);
          setSelectedTemplate(null);
          setAssociatedData(null);
          setAssociatedError(null);
        }}
      >
        <td className="px-6 py-4 whitespace-nowrap">
          <div className="text-sm font-medium text-gray-900">{category.name}</div>
          <div className="text-sm text-gray-500">{category.legacy_extrusora_name || category.description || 'Extrusora'}</div>
        </td>
        <td className="px-6 py-4 whitespace-nowrap">
          <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
            Extrusora
          </span>
        </td>
        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
          {Object.keys(category.product_classes).length} clases
        </td>
        <td className="px-6 py-4 whitespace-nowrap">
          <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">
            {category.templates} plantillas
          </span>
        </td>
        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
          {category.active_templates} activas
        </td>
        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
          <button className="text-blue-600 hover:text-blue-800">Ver</button>
        </td>
      </tr>
    ));
  };

  const renderProductClassRows = () => {
    if (templatesError) {
      return (
        <tr>
          <td colSpan={7} className="px-6 py-6 text-center text-sm text-red-600">
            {templatesError}
          </td>
        </tr>
      );
    }

    const entries = Object.entries(groupedByClass);
    if (!entries.length) {
      return (
        <tr>
          <td colSpan={7} className="px-6 py-6 text-center text-sm text-gray-500">
            No se encontraron plantillas para esta extrusora.
          </td>
        </tr>
      );
    }

    return entries.map(([productClass, classTemplates]) => (
      <tr
        key={productClass}
        className="hover:bg-gray-50 cursor-pointer"
        onClick={() => {
          setSelectedProductClass(productClass);
          setSelectedLine(null);
          setSelectedTemplate(null);
          setAssociatedData(null);
          setAssociatedError(null);
        }}
      >
        <td className="px-6 py-4 whitespace-nowrap">
          <div className="text-sm font-medium text-gray-900">{productClass}</div>
          <div className="text-sm text-gray-500">{classTemplates.length} plantillas</div>
        </td>
        <td className="px-6 py-4 whitespace-nowrap">{getClassBadge(productClass)}</td>
        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
          {new Set(classTemplates.map((template) => template.line_name)).size} líneas
        </td>
        <td className="px-6 py-4 whitespace-nowrap">
          <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
            {classTemplates.length} productos
          </span>
        </td>
        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
          {classTemplates.filter((template) => template.is_active).length} activas
        </td>
        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
          <button className="text-blue-600 hover:text-blue-800">Ver líneas</button>
        </td>
      </tr>
    ));
  };

  const renderLineRows = () => {
    const entries = Object.entries(lineGroups);
    if (!entries.length) {
      return (
        <tr>
          <td colSpan={7} className="px-6 py-6 text-center text-sm text-gray-500">
            No se encontraron líneas para esta clase.
          </td>
        </tr>
      );
    }

    return entries.map(([line, lineTemplates]) => (
      <tr
        key={line}
        className="hover:bg-gray-50 cursor-pointer"
        onClick={() => {
          setSelectedLine(line);
          setSelectedTemplate(null);
          setAssociatedData(null);
          setAssociatedError(null);
        }}
      >
        <td className="px-6 py-4 whitespace-nowrap">
          <div className="text-sm font-medium text-gray-900">{line}</div>
          <div className="text-sm text-gray-500">{lineTemplates.length} productos</div>
        </td>
        <td className="px-6 py-4 whitespace-nowrap">
          <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">
            Línea
          </span>
        </td>
        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
          {lineTemplates[0]?.product_class}
        </td>
        <td className="px-6 py-4 whitespace-nowrap">
          <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
            {lineTemplates.length} productos
          </span>
        </td>
        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
          {lineTemplates.filter((template) => template.is_active).length} activas
        </td>
        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
          <button className="text-blue-600 hover:text-blue-800">Ver productos</button>
        </td>
      </tr>
    ));
  };

  const renderTemplateRows = () => {
    if (!filteredTemplates.length) {
      return (
        <tr>
          <td colSpan={7} className="px-6 py-6 text-center text-sm text-gray-500">
            No se encontraron plantillas para la selección actual.
          </td>
        </tr>
      );
    }

    return filteredTemplates.map((template) => (
      <tr
        key={template.id}
        className={`hover:bg-gray-50 cursor-pointer ${selectedTemplate?.id === template.id ? 'bg-blue-50' : ''}`}
        onClick={() => handleSelectTemplate(template)}
      >
        <td className="px-6 py-4 whitespace-nowrap">
          <div className="text-sm font-medium text-gray-900">{template.code}</div>
        </td>
        <td className="px-6 py-4 whitespace-nowrap">{getClassBadge(template.product_class)}</td>
        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">v{template.version}</td>
        <td className="px-6 py-4 whitespace-nowrap">
          <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">
            {template.attributes_count ?? 0} atributos
          </span>
        </td>
        <td className="px-6 py-4 whitespace-nowrap">{getStatusBadge(template.is_active)}</td>
        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
          {template.created_at ? new Date(template.created_at).toLocaleDateString('es-AR') : '—'}
        </td>
        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
          <div className="flex justify-end gap-2">
            <button
              onClick={(event) => {
                event.stopPropagation();
                onPreview?.(template.id);
              }}
              className="text-gray-400 hover:text-gray-600"
              title="Vista previa"
            >
              <Eye size={16} />
            </button>
            <button
              onClick={(event) => {
                event.stopPropagation();
                onEdit?.(template.id);
              }}
              className="text-blue-600 hover:text-blue-800"
              title="Editar"
            >
              <Edit size={16} />
            </button>
            <button
              onClick={(event) => {
                event.stopPropagation();
                handleClone(template.id);
              }}
              className="text-indigo-600 hover:text-indigo-800"
              title="Duplicar"
            >
              <Copy size={16} />
            </button>
            <button
              onClick={(event) => {
                event.stopPropagation();
                handleDelete(template.id);
              }}
              className="text-red-600 hover:text-red-800"
              title="Eliminar"
            >
              <Trash2 size={16} />
            </button>
          </div>
        </td>
      </tr>
    ));
  };

  const renderTableBody = () => {
    if (selectedLine) {
      return renderTemplateRows();
    }
    if (selectedProductClass) {
      return renderLineRows();
    }
    if (selectedCategoryId !== null) {
      return renderProductClassRows();
    }
    return renderCategoryRows();
  };
  const loading = loadingCategories || (selectedCategoryId !== null && loadingTemplates);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    );
  }

  const categoryPageCount = Math.ceil(categories.length / ITEMS_PER_PAGE) || 1;

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-gray-900 mb-1">
            Plantillas de Producto
            {selectedCategoryName && (
              <span className="text-lg font-medium text-blue-600 ml-2">- {selectedCategoryName}</span>
            )}
          </h1>
          <p className="text-gray-600">
            {selectedCategoryName
              ? selectedProductClass
                ? selectedLine
                  ? 'Selecciona una plantilla para ver los detalles y accesorios relacionados.'
                  : 'Selecciona una línea para ver las plantillas disponibles.'
                : 'Selecciona una clase de producto para ver sus líneas.'
              : 'Selecciona una extrusora para comenzar.'}
          </p>
        </div>
        <div className="ml-4">
          <button
            onClick={() => setShowNewTemplateForm(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors whitespace-nowrap disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={!selectedCategoryId}
          >
            <Plus size={16} />
            Nueva Plantilla
          </button>
        </div>
      </div>

      <div className="bg-white rounded-lg border p-4 space-y-4">
        <div className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
            <input
              type="text"
              placeholder="Buscar por línea..."
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={!selectedCategoryId}
            />
          </div>
          <button
            onClick={() => setShowFilters((value) => !value)}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2"
          >
            <Filter size={16} />
            Filtros
          </button>
        </div>

        {showFilters && (
          <div className="grid grid-cols-2 gap-4 pt-4 border-t">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Estado</label>
              <select
                value={statusFilter}
                onChange={(event) => setStatusFilter(event.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Todos</option>
                <option value="true">Activos</option>
                <option value="false">Inactivos</option>
              </select>
            </div>
          </div>
        )}
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nombre</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tipo</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Detalle</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cantidad</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Info</th>
              <th className="px-6 py-3" />
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">{renderTableBody()}</tbody>
        </table>

        {!selectedCategoryId && categories.length > ITEMS_PER_PAGE && (
          <div className="px-6 py-3 border-t bg-gray-50 flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Mostrando {((currentPage - 1) * ITEMS_PER_PAGE) + 1} a {Math.min(currentPage * ITEMS_PER_PAGE, categories.length)} de {categories.length} categorías
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
                disabled={currentPage === 1}
                className="px-3 py-1 text-sm border rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Anterior
              </button>
              {Array.from({ length: categoryPageCount }, (_, index) => index + 1).map((page) => (
                <button
                  key={page}
                  onClick={() => setCurrentPage(page)}
                  className={`px-3 py-1 text-sm border rounded ${
                    currentPage === page ? 'bg-blue-600 text-white border-blue-600' : 'hover:bg-gray-100'
                  }`}
                >
                  {page}
                </button>
              ))}
              <button
                onClick={() => setCurrentPage((prev) => Math.min(prev + 1, categoryPageCount))}
                disabled={currentPage === categoryPageCount}
                className="px-3 py-1 text-sm border rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Siguiente
              </button>
            </div>
          </div>
        )}

        {selectedLine && (
          <div className="px-6 py-3 border-t bg-blue-50 flex items-center justify-between sticky bottom-0">
            <button
              onClick={() => setSelectedLine(null)}
              className="text-blue-600 hover:text-blue-800 font-medium"
            >
              ← Volver a líneas
            </button>
            <div className="text-sm text-gray-700">{selectedProductClass} - {selectedLine}</div>
          </div>
        )}

        {selectedProductClass && !selectedLine && (
          <div className="px-6 py-3 border-t bg-blue-50 flex items-center justify-between sticky bottom-0">
            <button
              onClick={() => setSelectedProductClass(null)}
              className="text-blue-600 hover:text-blue-800 font-medium"
            >
              ← Volver a clases
            </button>
            <div className="text-sm text-gray-700">Clase: {selectedProductClass}</div>
          </div>
        )}

        {selectedCategoryId !== null && !selectedProductClass && !selectedLine && (
          <div className="px-6 py-3 border-t bg-blue-50 flex items-center justify-between sticky bottom-0">
            <button
              onClick={() => {
                setSelectedCategoryId(null);
                setSelectedCategoryName('');
                setSelectedProductClass(null);
                setSelectedLine(null);
                setSelectedTemplate(null);
                setAssociatedData(null);
              }}
              className="text-blue-600 hover:text-blue-800 font-medium"
            >
              ← Volver a extrusoras
            </button>
            <div className="text-sm text-gray-700">Extrusora: {selectedCategoryName}</div>
          </div>
        )}
      </div>

      {selectedTemplate && (
        <div className="bg-white border rounded-lg shadow-sm p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">{selectedTemplate.code}</h2>
              <p className="text-sm text-gray-600">
                {selectedTemplate.product_class} · {selectedTemplate.line_name} · v{selectedTemplate.version}
              </p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => onPreview?.(selectedTemplate.id)}
                className="text-gray-500 hover:text-gray-700"
                title="Vista previa"
              >
                <Eye size={18} />
              </button>
              <button
                onClick={() => onEdit?.(selectedTemplate.id)}
                className="text-blue-600 hover:text-blue-800"
                title="Editar"
              >
                <Edit size={18} />
              </button>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 text-sm text-gray-700">
            <div>
              <span className="font-medium text-gray-900">Estado:</span> {selectedTemplate.is_active ? 'Activo' : 'Inactivo'}
            </div>
            <div>
              <span className="font-medium text-gray-900">Fecha creación:</span>{' '}
              {selectedTemplate.created_at ? new Date(selectedTemplate.created_at).toLocaleDateString('es-AR') : '—'}
            </div>
            <div>
              <span className="font-medium text-gray-900">Atributos:</span> {selectedTemplate.attributes_count ?? 0}
            </div>
            <div>
              <span className="font-medium text-gray-900">Categoría:</span> {selectedCategoryName || '—'}
            </div>
          </div>

          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-2">Accesorios relacionados</h3>
            {associatedLoading ? (
              <div className="text-sm text-gray-500">Cargando accesorios...</div>
            ) : associatedError ? (
              <div className="text-sm text-red-600">{associatedError}</div>
            ) : associatedData && associatedData.associated_products.length > 0 ? (
              <div className="overflow-hidden border border-gray-200 rounded-md">
                <table className="min-w-full text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left font-medium text-gray-600">Código</th>
                      <th className="px-4 py-2 text-left font-medium text-gray-600">Clase</th>
                      <th className="px-4 py-2 text-left font-medium text-gray-600">Línea</th>
                      <th className="px-4 py-2 text-left font-medium text-gray-600">Relación</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {associatedData.associated_products.map((product) => (
                      <tr key={`${product.relationship_type}-${product.id}`}>
                        <td className="px-4 py-2 whitespace-nowrap text-gray-800">{product.code}</td>
                        <td className="px-4 py-2 whitespace-nowrap text-gray-600">{product.product_class}</td>
                        <td className="px-4 py-2 whitespace-nowrap text-gray-600">{product.line_name}</td>
                        <td className="px-4 py-2 whitespace-nowrap text-gray-600">{product.relationship_type}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-sm text-gray-500">Esta plantilla no tiene accesorios asociados.</div>
            )}
          </div>
        </div>
      )}

      {showNewTemplateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-96 max-w-md mx-4">
            <h3 className="text-lg font-semibold mb-4">Nueva Plantilla</h3>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">Nombre de la Plantilla</label>
              <input
                type="text"
                value={newTemplateName}
                onChange={(event) => setNewTemplateName(event.target.value)}
                placeholder="Ej: Ventana A30 Corrediza"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                autoFocus
              />
            </div>

            <div className="flex gap-3 justify-end">
              <button
                onClick={() => {
                  setShowNewTemplateForm(false);
                  setNewTemplateName('');
                }}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancelar
              </button>
              <button
                onClick={handleCreateTemplate}
                disabled={!newTemplateName.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Crear Plantilla
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TemplateList;






