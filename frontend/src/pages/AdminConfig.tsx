import React from 'react';
import { GuardrailConfigPanel } from '../components/GuardrailConfigPanel';
import { useAuth } from '../context/AuthContext';
import { Navigate } from 'react-router-dom';

export const AdminConfig: React.FC = () => {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/admin/login" replace />;
  }

  return (
    <div className="space-y-6">
      <GuardrailConfigPanel />
    </div>
  );
};
