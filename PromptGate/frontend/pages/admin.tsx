import React from 'react';
import { AdminDashboard } from '../components/dashboard/AdminDashboard';

const AdminPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-50">
      <AdminDashboard />
    </div>
  );
};

export default AdminPage;