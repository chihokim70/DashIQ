import { useState, useEffect } from "react";
import { Header } from "./components/Header";
import { Sidebar } from "./components/Sidebar";
import { DashboardOverview } from "./components/pages/DashboardOverview";
import { PromptUsage } from "./components/pages/PromptUsage";
import { PolicyMonitor } from "./components/pages/PolicyMonitor";
import { ShadowAI } from "./components/pages/ShadowAI";
import { OnPremLLM } from "./components/pages/OnPremLLM";
import { ImageGeneration } from "./components/pages/ImageGeneration";
import { CaseManagement } from "./components/pages/CaseManagement";
import { Settings } from "./components/pages/Settings";

export default function App() {
  const [currentPage, setCurrentPage] = useState("dashboard");
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [darkMode]);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  const renderPage = () => {
    switch (currentPage) {
      case "dashboard":
        return <DashboardOverview />;
      case "prompt":
        return <PromptUsage />;
      case "policy":
        return <PolicyMonitor />;
      case "shadow":
        return <ShadowAI />;
      case "onprem":
        return <OnPremLLM />;
      case "image":
        return <ImageGeneration />;
      case "case":
        return <CaseManagement />;
      case "settings":
        return <Settings />;
      default:
        return <DashboardOverview />;
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="flex">
        <Sidebar currentPage={currentPage} onPageChange={setCurrentPage} />
        
        <div className="flex-1 flex flex-col">
          <Header darkMode={darkMode} toggleDarkMode={toggleDarkMode} />
          
          <main className="flex-1 overflow-auto">
            {renderPage()}
          </main>
        </div>
      </div>
    </div>
  );
}
