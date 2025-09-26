import React, { useState } from 'react';
import { Users, Shield, Settings as SettingsIcon } from 'lucide-react';
import UserList from './UserList';
import RoleList from './RoleList';

const SettingsLayout: React.FC = () => {
  const [activeTab, setActiveTab] = useState('users');

  const tabs = [
    { id: 'users', label: 'Usuarios', icon: Users },
    { id: 'roles', label: 'Roles', icon: Shield },
  ];

  return (
    <>
      <header className="bg-white shadow-sm border-b px-6 py-4">
        <div className="flex items-center">
          <SettingsIcon className="w-6 h-6 text-gray-600 mr-3" />
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Configuración</h2>
            <p className="text-gray-600">Gestión de usuarios y permisos</p>
          </div>
        </div>
      </header>

      <main className="flex-1 overflow-y-auto">
        <div className="bg-white border-b">
          <nav className="flex space-x-8 px-6">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  <Icon className="w-4 h-4 mr-2" />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'users' && <UserList />}
          {activeTab === 'roles' && <RoleList />}
        </div>
      </main>
    </>
  );
};

export default SettingsLayout;