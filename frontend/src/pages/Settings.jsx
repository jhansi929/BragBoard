import React, { useState, useEffect } from "react";
import Sidebar from "../components/Sidebar";
import axios from "axios";

export default function Settings() {
  const [user, setUser] = useState(null);
  const [name, setName] = useState("");
  const [department, setDepartment] = useState("");
  const [password, setPassword] = useState("");

  useEffect(() => {
    const fetchUserProfile = async () => {
      try {
        const token = localStorage.getItem("access_token");
        if (!token) return;

        const response = await axios.get("http://127.0.0.1:8000/me", {
          headers: { Authorization: `Bearer ${token}` },
        });

        setUser(response.data);
        setName(response.data.name);
        setDepartment(response.data.department);
      } catch (error) {
        console.error("Error loading profile:", error);
      }
    };

    fetchUserProfile();
  }, []);

  const handleProfileUpdate = async () => {
    try {
      const token = localStorage.getItem("access_token");
      if (!token) return alert("Please log in again.");

      const payload = {
        name,
        department,
        password: password || undefined,
      };

      await axios.put("http://127.0.0.1:8000/update-profile", payload, {
        headers: { Authorization: `Bearer ${token}` },
      });

      alert("✅ Profile updated successfully!");
      setPassword("");
    } catch (error) {
      console.error("Error updating profile:", error);
      alert("❌ Failed to update profile");
    }
  };

  const handleDeleteAccount = async () => {
    if (!window.confirm("⚠️ Are you sure you want to delete your account? This cannot be undone.")) {
      return;
    }

    try {
      const token = localStorage.getItem("access_token");
      if (!token) return alert("Please log in again.");

      await axios.delete("http://127.0.0.1:8000/delete-account", {
        headers: { Authorization: `Bearer ${token}` },
      });

      alert("🗑️ Account deleted successfully.");
      localStorage.clear();
      window.location.href = "/login";
    } catch (error) {
      console.error("Error deleting account:", error);
      alert("❌ Failed to delete account");
    }
  };

  if (!user) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-gray-900 text-white">
        <p>Loading settings...</p>
      </div>
    );
  }

  return (
    <div className="flex h-screen w-screen bg-gray-900 text-white overflow-hidden">
      <Sidebar />

      <div className="flex-1 p-10 overflow-y-auto ml-64">
        <h1 className="text-3xl font-bold mb-6 text-blue-400">Settings</h1>

        {/* Profile Settings */}
        <div className="bg-gray-800 p-6 rounded-2xl shadow-lg max-w-lg">
          <h2 className="text-xl font-semibold mb-4 text-blue-300">Profile Settings</h2>

          <label className="block mb-4">
            <span className="text-gray-300">Name:</span>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full mt-2 p-2 rounded bg-gray-700 text-white"
            />
          </label>

          <label className="block mb-4">
            <span className="text-gray-300">Department:</span>
            <input
              type="text"
              value={department}
              onChange={(e) => setDepartment(e.target.value)}
              className="w-full mt-2 p-2 rounded bg-gray-700 text-white"
            />
          </label>

          <label className="block mb-4">
            <span className="text-gray-300">Change Password (optional):</span>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full mt-2 p-2 rounded bg-gray-700 text-white"
              placeholder="New password"
            />
          </label>

          <button
            onClick={handleProfileUpdate}
            className="bg-green-500 hover:bg-green-600 text-white px-6 py-2 rounded-lg"
          >
            Update Profile
          </button>
        </div>

        {/* Account Settings */}
        <div className="bg-gray-800 p-6 rounded-2xl shadow-lg max-w-lg mt-6">
          <h2 className="text-xl font-semibold mb-4 text-blue-300">Account Management</h2>
          <p className="text-gray-400 mb-4 text-sm">
            You can delete your account permanently. This action cannot be undone.
          </p>
          <button
            onClick={handleDeleteAccount}
            className="bg-red-500 hover:bg-red-600 text-white px-6 py-2 rounded-lg"
          >
            Delete Account
          </button>
        </div>
      </div>
    </div>
  );
}
