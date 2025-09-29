import React from 'react';
import { LogOut, Users, ShoppingCart, Package, Home as HomeIcon, FileText, Settings, BarChart3 } from 'lucide-react';

interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
}

interface LayoutProps {
  user: User;
  onLogout: () => void;
  children: React.ReactNode;
  currentPath: string;
}

const Layout: React.FC<LayoutProps> = ({ user, onLogout, children, currentPath }) => {
  const handleLogout = async () => {
    try {
      await fetch(`${process.env.REACT_APP_API_URL}/api/logout/`, {
        method: 'POST',
        credentials: 'include'
      });
      onLogout();
    } catch (error) {
      console.error('Error logging out:', error);
      onLogout();
    }
  };

  const menuItems = [
    { icon: HomeIcon, label: 'Dashboard', path: '/' },
    { icon: Users, label: 'Clientes', path: '/clientes' },
    { icon: Package, label: 'Productos', path: '/productos' },
    { icon: ShoppingCart, label: 'Pedidos', path: '/pedidos' },
    { icon: FileText, label: 'Presupuestos', path: '/presupuestos' },
    { icon: BarChart3, label: 'Reportes', path: '/reportes' },
    { icon: Settings, label: 'Configuración', path: '/configuracion' },
  ];

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-64 bg-white shadow-lg flex flex-col">
        {/* Logo */}
        <div className="p-6 border-b text-center">
          <img 
            src="/AKUN-LOGO.webp" 
            alt="AKUN Logo" 
            className="h-12 w-auto mx-auto mb-2"
          />
          <p className="text-sm text-gray-600">Sistema de Gestión</p>
        </div>
        
        {/* Navigation */}
        <nav className="flex-1 p-4">
          <ul className="space-y-2">
            {menuItems.map((item, index) => {
              const Icon = item.icon;
              const isActive = currentPath === item.path;
              return (
                <li key={index}>
                  <button 
                    onClick={() => window.location.hash = item.path}
                    className={`w-full flex items-center px-3 py-2 text-left rounded-lg transition-colors ${
                      isActive 
                        ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700' 
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <Icon className="w-5 h-5 mr-3" />
                    {item.label}
                  </button>
                </li>
              );
            })}
          </ul>
        </nav>
        
        {/* User Info & Logout */}
        <div className="p-4 border-t">
          <div className="flex items-center mb-3">
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <span className="text-sm font-medium text-blue-700">
                {(user.first_name?.[0] || user.email[0]).toUpperCase()}
              </span>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-900">
                {user.first_name || user.email}
              </p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="w-full flex items-center px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <LogOut className="w-4 h-4 mr-3" />
            Cerrar Sesión
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {children}
      </div>
    </div>
  );
};

export default Layout;