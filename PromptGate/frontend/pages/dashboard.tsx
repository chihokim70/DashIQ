import React from 'react';
import ChatInterface from '@/components/prompt/ChatInterface';
import { DashboardStats } from '@/components/dashboard/DashboardStats';
import { DashboardCharts } from '@/components/dashboard/DashboardCharts';
import { RecentActivity } from '@/components/dashboard/RecentActivity';

const DashboardPage: React.FC = () => {
  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Use existing ChatInterface wrapper but with dashboard content */}
      <div className="flex-1">
        <ChatInterface showDashboard={true} />
      </div>
    </div>
  );
};

export default DashboardPage;