import React, { useState, useEffect } from 'react';
import Login from './Login';
import Home from './Home';
import CustomerList from './components/customers/CustomerList';
import CustomerForm from './components/customers/CustomerForm';
import CustomerDetail from './components/customers/CustomerDetail';
import CustomerEdit from './components/customers/CustomerEdit';
import ProductList from './components/products/ProductList';
import ProductForm from './components/products/ProductForm';
import QuoteList from './components/quotes/QuoteList';
import QuoteForm from './components/quotes/QuoteForm';
import OrderList from './components/orders/OrderList';
import SettingsLayout from './components/settings/SettingsLayout';
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
  const [loading, setLoading] = useState(true);
  const [currentPath, setCurrentPath] = useState(window.location.hash.slice(1) || '/');

  useEffect(() => {
    const handleHashChange = () => {
      setCurrentPath(window.location.hash.slice(1) || '/');
    };
    
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  useEffect(() => {
    checkSession();
  }, []);

  const checkSession = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/profile/`, {
        credentials: 'include'
      });
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      }
    } catch (error) {
      console.log('No hay sesión activa');
    } finally {
      setLoading(false);
    }
  };

  const handleLoginSuccess = (userData: User) => {
    setUser(userData);
  };

  const handleLogout = () => {
    setUser(null);
    window.location.hash = '/';
  };

  if (loading) {
    return (
      <div className="App flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

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
    if (currentPath === '/presupuestos') {
      return <QuoteList />;
    }
    if (currentPath === '/presupuestos/nuevo') {
      return (
        <QuoteForm 
          onBack={() => window.location.hash = '/presupuestos'}
          onSave={() => window.location.hash = '/presupuestos'}
        />
      );
    }
    if (currentPath === '/pedidos') {
      return <OrderList />;
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
    if (currentPath === '/configuracion') {
      return <SettingsLayout />;
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