import { useState } from "react";
import { AdminSidebar } from "./components/admin-sidebar";
import { DashboardSection } from "./components/dashboard-section";
import { UsersSection } from "./components/users-section";
import { RecognitionSection } from "./components/recognition-section";
import { SettingsSection } from "./components/settings-section";

export default function App() {
  const [activeSection, setActiveSection] = useState("dashboard");

  const renderSection = () => {
    switch (activeSection) {
      case "dashboard":
        return <DashboardSection />;
      case "users":
        return <UsersSection />;
      case "recognition":
        return <RecognitionSection />;
      case "settings":
        return <SettingsSection />;
      case "analytics":
      case "alerts":
      case "security":
        return (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <h2 className="text-2xl mb-2">Sección en Desarrollo</h2>
              <p className="text-muted-foreground">Esta sección estará disponible próximamente</p>
            </div>
          </div>
        );
      default:
        return <DashboardSection />;
    }
  };

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {/* Sidebar */}
      <AdminSidebar
        activeSection={activeSection}
        onSectionChange={setActiveSection}
      />

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <div className="p-4">
          {renderSection()}
        </div>
      </main>
    </div>
  );
}
