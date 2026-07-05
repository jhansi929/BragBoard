// src/components/Sidebar.jsx
import React from "react";
import { Link, useLocation } from "react-router-dom";

export default function Sidebar() {
  const { pathname } = useLocation();
  const userRole = (localStorage.getItem("user_role") || "").toLowerCase().trim();

  const linkClass = (path) =>
    `block py-2.5 px-4 rounded-xl transition font-medium ${
      pathname === path
        ? "bg-blue-600 text-white shadow-md"
        : "text-gray-200 hover:bg-gray-700 hover:text-white"
    }`;

  const handleLogout = () => {
    if (window.confirm("🚪 Are you sure you want to log out?")) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("user_role");
      alert("👋 Logged out successfully!");
      window.location.href = "/login";
    }
  };

  return (
    <div className="w-64 bg-gray-800 min-h-screen p-6 border-r border-gray-700 flex flex-col justify-between">
      <div>
        <h2 className="text-3xl font-extrabold text-blue-400 mb-6 tracking-wide">
          BragBoard
        </h2>

        <nav className="space-y-2">
          {userRole === "admin" ? (
            <>
              <Link to="/admin" className={linkClass("/admin")}>
                🏠 Admin Dashboard
              </Link>
              {/* ✅ NEW: Reported shoutouts link for admins */}
              <Link to="/admin/reports" className={linkClass("/admin/reports")}>
                🚨 Reported Shoutouts
              </Link>
              <Link to="/profile" className={linkClass("/profile")}>
                👤 Profile
              </Link>
              <Link to="/settings" className={linkClass("/settings")}>
                ⚙️ Settings
              </Link>
            </>
          ) : (
            <>
              <Link to="/dashboard" className={linkClass("/dashboard")}>
                🏠 Dashboard
              </Link>
              <Link to="/postshoutout" className={linkClass("/postshoutout")}>
                💬 Post Shoutout
              </Link>
              <Link to="/shoutouts" className={linkClass("/shoutouts")}>
                📢 Shoutout Feed
              </Link>
              <Link to="/profile" className={linkClass("/profile")}>
                👤 Profile
              </Link>
              <Link to="/settings" className={linkClass("/settings")}>
                ⚙️ Settings
              </Link>
            </>
          )}
        </nav>
      </div>

      <button
        onClick={handleLogout}
        className="mt-8 w-full py-2 bg-red-500 hover:bg-red-600 text-white rounded-xl font-semibold transition"
      >
        🚪 Logout
      </button>
    </div>
  );
}
