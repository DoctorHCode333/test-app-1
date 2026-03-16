import React from "react";
import { Avatar } from "primereact/avatar";

const Nav = ({ title = "DID Dashboard" }) => {
  return (
    <nav className="bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 shadow-xl border-b border-slate-700/50">
      <div className="px-6 py-4 relative">
        {/* Center Title - Absolutely positioned */}
        <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 flex items-center gap-3">
          <div className="bg-gradient-to-br from-cyan-500 to-blue-600 p-2 rounded-lg shadow-lg shadow-cyan-500/20">
            <i className="pi pi-phone text-white text-xl"></i>
          </div>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent">
            {title}
          </h1>
        </div>

        {/* Right - User Profile */}
        <div className="flex items-center justify-end">
          <Avatar
            icon="pi pi-user"
            size="large"
            shape="circle"
            className="bg-gradient-to-br from-cyan-500 to-blue-600 text-white shadow-lg shadow-cyan-500/30 cursor-pointer hover:scale-105 transition-transform"
          />
        </div>
      </div>
    </nav>
  );
};

export default Nav;