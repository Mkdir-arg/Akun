import React, { useState, useEffect } from 'react';
import Login from './Login';
import Home from './Home';
import CustomerList from './components/customers/CustomerList';
import CustomerForm from './components/customers/CustomerForm';
import CustomerDetail from './components/customers/CustomerDetail';
import CustomerEdit from './components/customers/CustomerEdit';
import ProductList from './components/products/ProductList';
import ProductForm from './components/products/ProductForm';
import Layout from './components/Layout';
import './index.css';

interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
}

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [currentPath, setCurrentPath] = useState(window.location.hash.slice(1) || '/');

  useEffect(() => {
    const handleHashChange = () => {
      setCurrentPath(window.location.hash.slice(1) || '/');
    };
    
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  const handleLoginSuccess = (userData: User) => {
    setUser(userData);
  };

  const handleLogout = () => {
    setUser(null);
    window.location.hash = '/';
  };

  if (!user) {
    return (
      <div className="App">
        <Login onLoginSuccess={handleLoginSuccess} />
      </div>
    );
  }

  const renderCurrentPage = () => {
    if (currentPath === '/clientes') {
      return <CustomerList />;
    }
    if (currentPath === '/productos') {
      return <ProductList />;
    }
    if (currentPath === '/productos/nuevo') {
      return (
        <ProductForm 
          onBack={() => window.location.hash = '/productos'}
          onSave={() => window.location.hash = '/productos'}
        />
      );
    }
    if (currentPath.startsWith('/productos/') && currentPath.endsWith('/editar')) {
      const productId = currentPath.split('/')[2];
      return (
        <ProductForm 
          productId={productId}
          onBack={() => window.location.hash = `/productos/${productId}`}
          onSave={() => window.location.hash = `/productos/${productId}`}
        />
      );
    }
    if (currentPath === '/clientes/nuevo') {
      return (
        <CustomerForm 
          onBack={() => window.location.hash = '/clientes'}
          onSave={() => window.location.hash = '/clientes'}
        />
      );
    }
    if (currentPath.startsWith('/clientes/') && currentPath.endsWith('/editar')) {
      const customerId = currentPath.split('/')[2];
      return (
        <CustomerEdit 
          customerId={customerId}
          onBack={() => window.location.hash = `/clientes/${customerId}`}
          onSave={() => window.location.hash = `/clientes/${customerId}`}
        />
      );
    }
    if (currentPath.startsWith('/clientes/') && !currentPath.endsWith('/editar') && currentPath !== '/clientes/nuevo') {
      const customerId = currentPath.split('/')[2];
      return (
        <CustomerDetail 
          customerId={customerId}
          onBack={() => window.location.hash = '/clientes'}
          onEdit={() => window.location.hash = `/clientes/${customerId}/editar`}
        />
      );
    }
    return <Home />;
  };

  return (
    <div className="App">
      <Layout user={user} onLogout={handleLogout} currentPath={currentPath}>
        {renderCurrentPage()}
      </Layout>
    </div>
  );
}

export default App;