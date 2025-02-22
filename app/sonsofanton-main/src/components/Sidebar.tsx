import { useNavigate, useLocation } from "react-router-dom";
import { Home, Newspaper, Clock, Star, Settings, Menu } from "lucide-react";
import { useState } from "react";
export default function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const navItems = [{
    icon: Home,
    label: "For You",
    path: "/"
  }, {
    icon: Newspaper,
    label: "Latest",
    path: "/latest"
  }, {
    icon: Clock,
    label: "History",
    path: "/history"
  }, {
    icon: Star,
    label: "Saved",
    path: "/saved"
  }];
  return <div className={`fixed left-0 top-0 z-50 h-full bg-card transition-all duration-300 ${isCollapsed ? "w-16" : "w-64"} hidden lg:block lg:p-4`}>
      <button onClick={() => setIsCollapsed(!isCollapsed)} className="mb-8 flex w-full items-center gap-2 text-lg font-bold">
        <Menu className="h-6 w-6" />
        {!isCollapsed && <span>Sons of Anton</span>}
      </button>

      <nav className="space-y-2">
        {navItems.map(item => <button key={item.path} onClick={() => navigate(item.path)} className={`nav-item w-full ${location.pathname === item.path ? "active" : ""}`}>
            <item.icon className="h-5 w-5" />
            {!isCollapsed && <span>{item.label}</span>}
          </button>)}
      </nav>

      <button onClick={() => navigate("/settings")} className={`nav-item absolute bottom-4 w-[calc(100%-2rem)]`}>
        <Settings className="h-5 w-5" />
        {!isCollapsed && <span>Settings</span>}
      </button>
    </div>;
}