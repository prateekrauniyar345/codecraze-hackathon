import { authAPI } from '../api/client';
import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        // Just call getMe. Axios sends the cookie automatically.
        const response = await authAPI.getMe();
        setUser(response.data);
      } catch (error) {
        console.log("No active session found.");
        setUser(null);
      } finally {
        setLoading(false);
      }
    };
    checkAuth();
  }, []);

  const login = () => {
    // Redirect to the backend OAuth start point
    window.location.href = `${import.meta.env.VITE_API_URL}/auth/login`;
  };

  const logout = async () => {
    try {
      await authAPI.logout(); // Backend will clear the HttpOnly cookie
    } catch (err) {
      console.error("Logout failed", err);
    } finally {
      setUser(null);
      window.location.href = '/login';
    }
  };

  const value = {
    user,
    loading,
    login,
    logout,
    isAuthenticated: !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children} 
    </AuthContext.Provider>
  );
};