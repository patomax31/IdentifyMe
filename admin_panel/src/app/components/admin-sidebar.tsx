import { LayoutDashboard, Users, ScanFace, Settings, Bell, BarChart3, Shield } from "lucide-react";
import { cn } from "./ui/utils";

interface AdminSidebarProps {
  activeSection: string;
  onSectionChange: (section: string) => void;
}

export function AdminSidebar({ activeSection, onSectionChange }: AdminSidebarProps) {
  const menuItems = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "users", label: "Usuarios", icon: Users },
    { id: "recognition", label: "Reconocimientos", icon: ScanFace },
    { id: "analytics", label: "Análisis", icon: BarChart3 },
    { id: "alerts", label: "Alertas", icon: Bell },
    { id: "security", label: "Seguridad", icon: Shield },
    { id: "settings", label: "Configuración", icon: Settings },
  ];

  return (
    <aside className="w-48 bg-gradient-to-b from-[#164e63] to-[#0e3f52] text-white h-screen flex flex-col shadow-2xl">
      {/* Logo */}
      <div className="p-4 border-b border-cyan-800/30">
        <div className="flex flex-col items-center gap-2">
          <div className="w-10 h-10 bg-gradient-to-br from-primary to-cyan-400 rounded-xl flex items-center justify-center shadow-lg shadow-cyan-500/50">
            <ScanFace className="w-5 h-5" />
          </div>
          <div className="text-center">
            <h1 className="text-base font-bold bg-gradient-to-r from-white to-cyan-200 bg-clip-text text-transparent">
              Escuela
            </h1>
            <p className="text-xs text-cyan-200/80">Control Acceso</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-2 overflow-y-auto">
        <ul className="space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeSection === item.id;
            return (
              <li key={item.id}>
                <button
                  onClick={() => onSectionChange(item.id)}
                  className={cn(
                    "w-full flex flex-col items-center gap-1 px-2 py-2.5 rounded-lg transition-all duration-200 group relative overflow-hidden",
                    isActive
                      ? "bg-gradient-to-r from-primary to-cyan-400 text-white shadow-lg shadow-cyan-500/30"
                      : "text-cyan-100 hover:bg-white/10"
                  )}
                >
                  {isActive && (
                    <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent" />
                  )}
                  <Icon className={cn(
                    "w-5 h-5 relative z-10 transition-transform",
                    isActive ? "scale-110" : "group-hover:scale-110"
                  )} />
                  <span className="relative z-10 font-medium text-xs text-center">{item.label}</span>
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Footer */}
      <div className="p-3 border-t border-cyan-800/30">
        <div className="flex flex-col items-center gap-2 px-2 py-2 rounded-xl bg-white/5 hover:bg-white/10 transition-colors cursor-pointer">
          <div className="w-9 h-9 bg-gradient-to-br from-primary to-cyan-400 rounded-full flex items-center justify-center shadow-md">
            <span className="text-sm font-bold">A</span>
          </div>
          <div className="text-center">
            <p className="text-xs font-semibold">Admin</p>
          </div>
        </div>
      </div>
    </aside>
  );
}