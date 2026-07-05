import React, { useState, useEffect, useCallback, useMemo } from "react";
import axios from "axios";
import Sidebar from "../components/Sidebar";

export default function ReportedShoutouts() {
  const [reports, setReports] = useState([]);

  // ✅ Stable headers across renders
  const headers = useMemo(() => {
    return {
      Authorization: `Bearer ${localStorage.getItem("access_token")}`,
    };
  }, []);

  // ✅ Stable fetch function
  const fetchReports = useCallback(async () => {
    try {
      const res = await axios.get("http://127.0.0.1:8000/reports", { headers });
      setReports(res.data);
    } catch (err) {
      console.error("Error fetching reports:", err);
      alert(err.response?.data?.detail || "❌ Failed to load reports.");
    }
  }, [headers]);

  // ✅ Single clean effect
  useEffect(() => {
    fetchReports();
  }, [fetchReports]);

  // ✅ Handle report resolution (delete shoutout)
  const handleResolve = async (id) => {
    if (!window.confirm("Are you sure you want to delete this reported shoutout?")) return;
    try {
      await axios.delete(`http://127.0.0.1:8000/reports/${id}/resolve`, { headers });
      setReports((prev) => prev.filter((r) => r.id !== id));
      alert("✅ Shoutout deleted successfully!");
    } catch (err) {
      console.error("Error resolving report:", err);
      alert(err.response?.data?.detail || "❌ Failed to delete shoutout.");
    }
  };

  return (
    <div className="flex h-screen w-screen bg-gray-900 text-white overflow-hidden">
      <Sidebar />
      <main className="flex-1 px-8 py-10 overflow-y-auto">
        <h1 className="text-3xl font-bold mb-8 text-red-400 text-center">
          🚨 Reported Shoutouts
        </h1>

        {reports.length === 0 ? (
          <p className="text-center text-gray-400">No reported shoutouts 🎉</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {reports.map((r) => (
              <div
                key={r.id}
                className="bg-gray-800 p-6 rounded-2xl shadow-lg border border-gray-700 hover:bg-gray-750 transition"
              >
                <p className="text-blue-400 font-semibold">{r.sender_name}</p>
                <p className="text-gray-300 mt-3 leading-relaxed">{r.message}</p>

                {r.image_url && (
                  <img
                    src={`http://127.0.0.1:8000${r.image_url}`}
                    alt="shoutout"
                    className="mt-3 rounded-xl max-h-48 object-cover"
                  />
                )}

                <p className="text-xs text-gray-500 mt-2">
                  {new Date(r.created_at).toLocaleString()}
                </p>

                <p className="text-xs text-yellow-400 mt-2">
                  Reported by <b>{r.reporter_name}</b> — Reason: {r.reason}
                </p>

                <button
                  onClick={() => handleResolve(r.id)}
                  className="mt-4 bg-red-600 hover:bg-red-700 px-3 py-1 rounded-xl text-sm"
                >
                  🗑 Delete Shoutout
                </button>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
