import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export interface AuthUser {
  name: string;
  email: string;
}

export type AuthView = 'landing' | 'login' | 'signup' | 'app';

interface AuthContextType {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isGuest: boolean;
  currentAuthView: AuthView;
  setCurrentAuthView: (view: AuthView) => void;
  login: (email: string, pass: string) => Promise<{ success: boolean; error?: string }>;
  signup: (name: string, email: string, pass: string) => Promise<{ success: boolean; error?: string }>;
  continueAsGuest: () => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const AUTH_STORAGE_KEY = 'f2f_auth_session_v1';

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isGuest, setIsGuest] = useState<boolean>(false);
  const [currentAuthView, setCurrentAuthView] = useState<AuthView>('landing');

  // Load session from localStorage
  useEffect(() => {
    try {
      const stored = localStorage.getItem(AUTH_STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        if (parsed.user && (parsed.isAuthenticated || parsed.isGuest)) {
          setUser(parsed.user);
          setIsAuthenticated(true);
          setIsGuest(!!parsed.isGuest);
          setCurrentAuthView('app');
        }
      }
    } catch (e) {
      console.error('Failed to restore auth session:', e);
    }
  }, []);

  const saveSession = (u: AuthUser | null, isAuth: boolean, guest: boolean) => {
    setUser(u);
    setIsAuthenticated(isAuth);
    setIsGuest(guest);
    if (isAuth) {
      setCurrentAuthView('app');
    }
    try {
      if (isAuth && u) {
        localStorage.setItem(
          AUTH_STORAGE_KEY,
          JSON.stringify({ user: u, isAuthenticated: isAuth, isGuest: guest })
        );
      } else {
        localStorage.removeItem(AUTH_STORAGE_KEY);
      }
    } catch (e) {
      console.error('Failed to persist auth session:', e);
    }
  };

  const login = async (email: string, pass: string): Promise<{ success: boolean; error?: string }> => {
    // Basic validation
    const trimmedEmail = email.trim();
    if (!trimmedEmail) {
      return { success: false, error: 'Please enter a valid email address.' };
    }
    if (!trimmedEmail.includes('@') || !trimmedEmail.includes('.')) {
      return { success: false, error: 'Please enter a valid email format.' };
    }
    if (!pass || pass.length < 4) {
      return { success: false, error: 'Password must be at least 4 characters long.' };
    }

    // Derive name from email if logging in
    const namePart = trimmedEmail.split('@')[0];
    const formattedName = namePart.charAt(0).toUpperCase() + namePart.slice(1);
    
    // Set user as Disha Sinha if matching or default nicely formatted
    const displayName = trimmedEmail.toLowerCase() === 'disha.sinha2612@gmail.com' ? 'Disha Sinha' : formattedName;

    const authUser: AuthUser = {
      name: displayName,
      email: trimmedEmail,
    };

    saveSession(authUser, true, false);
    return { success: true };
  };

  const signup = async (name: string, email: string, pass: string): Promise<{ success: boolean; error?: string }> => {
    const trimmedName = name.trim();
    const trimmedEmail = email.trim();

    if (!trimmedName) {
      return { success: false, error: 'Full Name is required.' };
    }
    if (!trimmedEmail || !trimmedEmail.includes('@') || !trimmedEmail.includes('.')) {
      return { success: false, error: 'Please enter a valid email address.' };
    }
    if (!pass || pass.length < 6) {
      return { success: false, error: 'Password must be at least 6 characters long.' };
    }

    const authUser: AuthUser = {
      name: trimmedName,
      email: trimmedEmail,
    };

    saveSession(authUser, true, false);
    return { success: true };
  };

  const continueAsGuest = () => {
    const guestUser: AuthUser = {
      name: 'Guest Chef',
      email: 'guest@fridge2feast.ai',
    };
    saveSession(guestUser, true, true);
  };

  const logout = () => {
    saveSession(null, false, false);
    setCurrentAuthView('landing');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        isGuest,
        currentAuthView,
        setCurrentAuthView,
        login,
        signup,
        continueAsGuest,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
