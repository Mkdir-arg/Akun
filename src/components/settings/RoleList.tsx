import React, { useState, useEffect } from 'react';
import { Search, Plus, Shield, Check, X } from 'lucide-react';

interface Role {
  id: number;
  name: string;
  description: string;
  can_access_crm: boolean;
  can_access_catalog: boolean;
  can_access_orders: boolean;
  can_access_quotes: boolean;
  can_access_reports: boolean;
  can_access_settings: boolean;
  can_create: boolean;
  can_edit: boolean;
  can_delete: boolean;
  can_export: boolean;
  is_active: boolean;
}

const RoleList: React.FC = () => {
  const [roles, setRoles] = useState<Role[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchRoles();
  }, [searchTerm]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchRoles = async () => {
    try {
      const params = new URLSearchParams();
      if (searchTerm) params.append('search', searchTerm);

      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/roles/?${params}`, {
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        setRoles(data.results || data);
      }
    } catch (error) {
      console.error('Error fetching roles:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleRoleStatus = async (roleId: number, isActive: boolean) => {
    try {
      const action = isActive ? 'deactivate' : 'activate';
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/roles/${roleId}/${action}/`, {
        method: 'POST',
        credentials: 'include'
      });

      if (response.ok) {
        fetchRoles();
      }
    } catch (error) {
      console.error('Error toggling role status:', error);
    }
  };

  const getStatusBadge = (isActive: boolean) => {
    return isActive 
      ? 'bg-green-100 text-green-800' 
      : 'bg-red-100 text-red-800';
  };

  const PermissionIcon: React.FC<{ hasPermission: boolean }> = ({ hasPermission }) => (
    hasPermission ? (
      <Check className="w-4 h-4 text-green-600" />
    ) : (
      <X className="w-4 h-4 text-red-400" />
    )
  );

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Buscar roles..."
            className="pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        
        <button className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700">
          <Plus className="w-4 h-4 mr-2" />
          Nuevo Rol
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {roles.map((role) => (
          <div key={role.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <Shield className="w-6 h-6 text-blue-600 mr-3" />
                <div>
                  <h3 className="text-lg font-medium text-gray-900">{role.name}</h3>
                  <p className="text-sm text-gray-500">{role.description}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusBadge(role.is_active)}`}>
                  {role.is_active ? 'Activo' : 'Inactivo'}
                </span>
                <button
                  onClick={() => toggleRoleStatus(role.id, role.is_active)}
                  className="text-blue-600 hover:text-blue-800 text-sm"
                >
                  {role.is_active ? 'Desactivar' : 'Activar'}
                </button>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">Acceso a Módulos</h4>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div className="flex items-center justify-between">
                    <span>CRM</span>
                    <PermissionIcon hasPermission={role.can_access_crm} />
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Catálogo</span>
                    <PermissionIcon hasPermission={role.can_access_catalog} />
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Pedidos</span>
                    <PermissionIcon hasPermission={role.can_access_orders} />
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Presupuestos</span>
                    <PermissionIcon hasPermission={role.can_access_quotes} />
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Reportes</span>
                    <PermissionIcon hasPermission={role.can_access_reports} />
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Configuración</span>
                    <PermissionIcon hasPermission={role.can_access_settings} />
                  </div>
                </div>
              </div>

              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">Permisos</h4>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div className="flex items-center justify-between">
                    <span>Crear</span>
                    <PermissionIcon hasPermission={role.can_create} />
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Editar</span>
                    <PermissionIcon hasPermission={role.can_edit} />
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Eliminar</span>
                    <PermissionIcon hasPermission={role.can_delete} />
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Exportar</span>
                    <PermissionIcon hasPermission={role.can_export} />
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t">
                <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                  Editar Rol
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {roles.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">No se encontraron roles</p>
        </div>
      )}
    </div>
  );
};

export default RoleList;