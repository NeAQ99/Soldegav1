// src/contexts/AuthContext.js
import React, { createContext, useState, useEffect } from 'react';
import axiosInstance from '../api/axiosInstance';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);

  // Simula la carga del usuario, por ejemplo, desde un endpoint de "auth/me/"
  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await axiosInstance.get('auth/me/');
        setUser(response.data);
      } catch (error) {
        console.error('Error al cargar el usuario:', error);
        setUser(null);
      }
    };
    fetchUser();
  }, []);

  return (
    <AuthContext.Provider value={{ user, setUser }}>
      {children}
    </AuthContext.Provider>
  );
};
