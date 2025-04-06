// src/pages/auth/callback.jsx
import { useEffect } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { useNavigate } from 'react-router-dom';

export default function AuthCallback() {
  const { handleRedirectCallback } = useAuth0();
  const navigate = useNavigate();

  useEffect(() => {
    const handleAuth = async () => {
      await handleRedirectCallback();
      navigate('/home'); // Redirect to home after auth
    };
    handleAuth();
  }, [handleRedirectCallback, navigate]);

  return <div>Loading...</div>;
}