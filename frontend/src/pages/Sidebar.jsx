import React from "react";
import {
  BookOpen, Calendar, Search, Settings, LogOut,
  LayoutDashboard, Users, BarChart2, GraduationCap
} from "lucide-react";
import { logout, getStoredUser } from "@/api";
import { useNavigate } from "react-router-dom";

const NAV = {
  student: [
    { name: "My Courses",    icon: BookOpen },
    { name: "Calendar",      icon: Calendar },
    { name: "Course Search", icon: Search },
    { name: "Settings",      icon: Settings },
  ],
  lecturer: [
    { name: "My Courses",    icon: BookOpen },
    { name: "Calendar",      icon: Calendar },
    { name: "Settings",      icon: Settings },
  ],
  admin: [
    { name: "Dashboard",     icon: LayoutDashboard },
    { name: "Courses",       icon: BookOpen },
    { name: "Users",         icon: Users },
    { name: "Reports",       icon: BarChart2 },
    { name: "Settings",      icon: Settings },
  ],
};

export default function Sidebar({ activeTab, setActiveTab }) {
  const navigate = useNavigate();
  const user = getStoredUser();
  const role = user?.accessLvl || "student";
  const items = NAV[role] || NAV.student;

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="flex w-[72px] shrink-0 flex-col items-center bg-indigo-600 py-6 min-h-screen">
      {/* Logo */}
      <div className="mb-5 flex h-11 w-11 items-center justify-center rounded-[14px] bg-white shadow-md">
        <GraduationCap size={24} className="text-indigo-600" />
      </div>

      {/* Nav items */}
      <div className="flex flex-1 flex-col items-center gap-2">
        {items.map((item) => {
          const Icon = item.icon;
          const active = activeTab === item.name;
          return (
            <button
              key={item.name}
              title={item.name}
              onClick={() => setActiveTab(item.name)}
              className={`flex h-11 w-11 items-center justify-center rounded-xl transition-all ${
                active
                  ? "bg-white/20"
                  : "hover:bg-white/10"
              }`}
            >
              <Icon size={20} color="#fff" opacity={active ? 1 : 0.7} strokeWidth={active ? 2.5 : 2} />
            </button>
          );
        })}
      </div>

      {/* Logout */}
      <button
        title="Logout"
        onClick={handleLogout}
        className="flex h-11 w-11 items-center justify-center rounded-xl hover:bg-white/10 transition-all"
      >
        <LogOut size={20} color="#fff" opacity={0.7} />
      </button>
    </div>
  );
}

