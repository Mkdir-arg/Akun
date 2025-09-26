interface User {
  id: string;
  email: string;
  password: string;
  role: 'superadmin' | 'admin' | 'user';
  createdAt: string;
}

const SUPER_ADMIN: User = {
  id: '1',
  email: 'admin@admin.com',
  password: 'admin123',
  role: 'superadmin',
  createdAt: new Date().toISOString()
};

export const initializeSuperAdmin = (): void => {
  const users = JSON.parse(localStorage.getItem('users') || '[]');
  const superAdminExists = users.find((user: User) => user.role === 'superadmin');
  
  if (!superAdminExists) {
    users.push(SUPER_ADMIN);
    localStorage.setItem('users', JSON.stringify(users));
    console.log('✅ Super Admin creado:', SUPER_ADMIN.email);
  } else {
    console.log('✅ Super Admin ya existe');
  }
};

export const authenticate = (email: string, password: string): User | null => {
  const users: User[] = JSON.parse(localStorage.getItem('users') || '[]');
  const user = users.find(u => u.email === email && u.password === password);
  
  if (user) {
    localStorage.setItem('currentUser', JSON.stringify(user));
    return user;
  }
  return null;
};