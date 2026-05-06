'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { User, getMe } from '@/lib/api';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  loginState: (token: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  const fetchUser = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      setLoading(false);
      // Redirect to login if on protected route
      if (pathname !== '/login' && pathname !== '/register') {
        router.push('/login');
      }
      return;
    }

    try {
      const userData = await getMe();
      setUser(userData);
      // Redirect to home if on auth pages
      if (pathname === '/login' || pathname === '/register') {
        router.push('/');
      }
    } catch (error) {
      console.error('Failed to fetch user', error);
      localStorage.removeItem('token');
      if (pathname !== '/login' && pathname !== '/register') {
        router.push('/login');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUser();
  }, [pathname]);

  const loginState = (token: string) => {
    localStorage.setItem('token', token);
    fetchUser();
    router.push('/');
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    router.push('/login');
  };

  return (
    <AuthContext.Provider value={{ user, loading, loginState, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
