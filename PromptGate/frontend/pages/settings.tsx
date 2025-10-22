import React from 'react';
import ChatInterface from '@/components/prompt/ChatInterface';

const SettingsPage: React.FC = () => {
  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <div className="flex-1">
        <ChatInterface showSettings={true} />
      </div>
    </div>
  );
};

export default SettingsPage;