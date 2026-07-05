// src/pages/dashboard.jsx
import React, { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import { useNavigate } from "react-router-dom";
import API from "../api/axios"; // ✅ consistent Axios instance

export default function Dashboard() {
  const [stats, setStats] = useState({
    total_shoutouts: 0,
    followers: 0,
    posts_today: 0,
    recent_activity: [],
  });
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await API.get("/dashboard-stats");
        console.log("✅ Dashboard stats:", res.data);

        setStats({
          total_shoutouts: res.data.total_shoutouts || 0,
          team_members: res.data.team_members || 0,
          posts_today: res.data.posts_today || 0,
          recent_activity: Array.isArray(res.data.recent_activity)
            ? res.data.recent_activity
            : [],
        });
      } catch (err) {
        console.error("Error fetching stats:", err);
        if (err.response?.status === 401) {
          console.warn("Dashboard 401:", err.response);
          // localStorage.removeItem("access_token");
          // navigate("/login");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [navigate]);

  if (loading) {
    return (
      <div className="flex h-screen w-screen bg-gray-900 text-white items-center justify-center">
        <p>Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className="flex h-screen w-screen bg-gray-900 text-white overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col items-center justify-start p-10 overflow-y-auto">
        <div className="w-full max-w-7xl">
          <h1 className="text-4xl font-extrabold mb-8 text-center text-blue-400">
            Welcome to Your Dashboard 👋
          </h1>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="bg-gray-800 p-6 rounded-2xl text-center shadow-lg hover:bg-gray-700 transition">
              <h2 className="text-lg font-semibold mb-2">My Shoutouts</h2>
              <p className="text-4xl font-bold text-blue-400">
                {stats.total_shoutouts}
              </p>
            </div>
            <div className="bg-gray-800 p-6 rounded-2xl text-center shadow-lg hover:bg-gray-700 transition">
              <h2 className="text-lg font-semibold mb-2">Team Members</h2>
              <p className="text-4xl font-bold text-blue-400">
                {stats.team_members}
              </p>
            </div>
            <div className="bg-gray-800 p-6 rounded-2xl text-center shadow-lg hover:bg-gray-700 transition">
              <h2 className="text-lg font-semibold mb-2">Posts Today</h2>
              <p className="text-4xl font-bold text-blue-400">
                {stats.posts_today}
              </p>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="mt-10 bg-gray-800 p-6 rounded-2xl shadow-lg">
            <h2 className="text-2xl font-semibold mb-4 text-blue-300">
              Recent Activity
            </h2>
            <ul className="space-y-3 text-gray-300">
              {Array.isArray(stats.recent_activity) &&
              stats.recent_activity.length > 0 ? (
                stats.recent_activity.map((item, idx) => (
                  <li key={idx}>
                    💬{" "}
                    <span className="text-blue-400">
                      {item.sender_name || "Someone"}
                    </span>
                    : {item.message || "No message"}
                  </li>
                ))
              ) : (
                <li>No recent activity yet.</li>
              )}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
