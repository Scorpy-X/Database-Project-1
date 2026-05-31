import React from "react";
import { getStoredUser, logout } from "@/api";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";

import { Separator } from "@/components/ui/separator";
import { LogOut, User, Mail, Hash, Shield } from "lucide-react";

export default function SettingsPage() {
  const user = getStoredUser();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const roleColor = {
    admin: "bg-red-100 text-red-700",
    lecturer: "bg-indigo-100 text-indigo-700",
    student: "bg-emerald-100 text-emerald-700",
  };

  return (
    <div className="flex flex-col gap-6 max-w-[520px]">
      <div>
        <h1 className="text-[24px] font-extrabold text-slate-900">Settings</h1>
        <p className="text-[13px] text-slate-400 mt-1">Your account information</p>
      </div>

      {/* Profile card */}
      <div className="rounded-xl border border-slate-200 bg-white overflow-hidden">
        <div className="bg-indigo-600 h-20" />
        <div className="px-6 pb-6">
          <div className="-mt-8 mb-4 flex h-16 w-16 items-center justify-center rounded-full border-4 border-white bg-indigo-100">
            <User size={28} className="text-indigo-600" />
          </div>
          <h2 className="text-[18px] font-extrabold text-slate-900">
            {user?.fname} {user?.lname}
          </h2>
          <span className={`inline-block mt-1 rounded-full px-3 py-0.5 text-[11px] font-bold capitalize ${roleColor[user?.accessLvl] || "bg-slate-100 text-slate-600"}`}>
            {user?.accessLvl}
          </span>
        </div>

        <Separator />

        <div className="flex flex-col gap-4 px-6 py-5">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-100">
              <Mail size={14} className="text-slate-500" />
            </div>
            <div>
              <p className="text-[11px] text-slate-400 font-semibold uppercase tracking-wide">Email</p>
              <p className="text-[13px] font-semibold text-slate-800">{user?.email}</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-100">
              <Hash size={14} className="text-slate-500" />
            </div>
            <div>
              <p className="text-[11px] text-slate-400 font-semibold uppercase tracking-wide">User ID</p>
              <p className="text-[13px] font-semibold text-slate-800">{user?.userID}</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-100">
              <Shield size={14} className="text-slate-500" />
            </div>
            <div>
              <p className="text-[11px] text-slate-400 font-semibold uppercase tracking-wide">Role</p>
              <p className="text-[13px] font-semibold text-slate-800 capitalize">{user?.accessLvl}</p>
            </div>
          </div>
        </div>
      </div>

      <Button
        variant="destructive"
        onClick={handleLogout}
        className="flex items-center gap-2 w-fit"
      >
        <LogOut size={15} /> Sign Out
      </Button>
    </div>
  );
}
