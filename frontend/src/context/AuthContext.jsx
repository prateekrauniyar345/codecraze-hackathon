import { authAPI, setAuthHeader } from '../api/client';
import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Initialize auth state from localStorage
    const initializeAuth = () => {
      const token = localStorage.getItem('token');
      console.log("token is : ", token);
      const savedUser = localStorage.getItem('user');
      console.log("saved user is : ", savedUser);
      
      if (token && savedUser) {
        try {
          const parsedUser = JSON.parse(savedUser);
          if (parsedUser) {
            // Set header FIRST before setting user state
            setAuthHeader(token);
            setUser(parsedUser);
            console.log('Auth restored from localStorage:', parsedUser.email);
          }
        } catch (error) {
          console.error("Failed to parse user from localStorage", error);
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          setAuthHeader(null);
        }
      }
      setLoading(false);
    };
    
    initializeAuth();
  }, []);

  const login = async (email, password) => {
    try {
      const response = await authAPI.login({ email, password });
      console.log("login responss is : ", response);
      const { access_token, user: userData } = response.data;
      
      console.log('Login successful for:', userData.email);
      
      if (access_token && userData) {
        // CRITICAL: Set auth header BEFORE updating state
        // This ensures subsequent API calls have the token
        setAuthHeader(access_token);
        localStorage.setItem('token', access_token);
        localStorage.setItem('user', JSON.stringify(userData));
        
        // Set user state last
        setUser(userData);
        
        return userData;
      } else {
        console.error("Login response missing token or user data", response.data);
        throw new Error("Login failed: Invalid response from server.");
      }
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const register = async (email, password, fullName) => {
    const response = await authAPI.register({
      email,
      password,
      full_name: fullName,
    });
    // const { access_token, user: userData } = response.data;
    
    // if (access_token && userData) {
    //   setAuthHeader(access_token);
    //   localStorage.setItem('token', access_token);
    //   localStorage.setItem('user', JSON.stringify(userData));
    //   setUser(userData);
    //   return userData;
    // } else {
    //   console.error("Register response missing token or user data", response.data);
    //   throw new Error("Registration failed: Invalid response from server.");
    // }
    return response.data;
  };

  const logout = () => {
    setAuthHeader(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
