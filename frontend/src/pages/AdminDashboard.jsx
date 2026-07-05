import Sidebar from "../components/Sidebar";
import { useEffect, useState } from "react";
import axios from "axios";

export default function AdminDashboard() {
  const [contributors, setContributors] = useState([]);
  const [tags, setTags] = useState([]);

  useEffect(() => {
    const token = localStorage.getItem("access_token");

    axios
      .get("http://localhost:8000/admin/dashboard", {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((res) => {
        setContributors(res.data.top_contributors);
        setTags(res.data.most_tagged);
      })
      .catch((err) => console.error(err));
  }, []);

  const handleExport = (type) => {
    const token = localStorage.getItem("access_token");
    const url = `http://127.0.0.1:8000/admin/reports/export/${type}`;

    // Open in a new tab with token
    window.open(`${url}?token=${token}`, "_blank");
  };

  return (
    <div className="flex h-screen w-screen bg-gray-900 text-white overflow-hidden">
      <Sidebar />

      <div className="flex-1 flex flex-col items-center justify-start p-10 overflow-y-auto">
        <div className="w-full max-w-7xl">
          <h1 className="text-4xl font-extrabold mb-8 text-center text-blue-400">
            Admin Dashboard
          </h1>

          {/* ✅ Export Buttons */}
          <div className="flex gap-4 mb-6 justify-center">
  <button
    onClick={() => window.open("http://127.0.0.1:8000/admin/export/csv", "_blank")}
    className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded-xl"
  >
    📄 Export CSV
  </button>
  <button
    onClick={() => window.open("http://127.0.0.1:8000/admin/export/pdf", "_blank")}
    className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded-xl"
  >
    🧾 Export PDF
  </button>
</div>


          {/* Top Contributors */}
          <div className="bg-gray-800 p-6 rounded-2xl shadow-lg mb-8">
            <h2 className="text-2xl font-semibold mb-4 text-blue-300">
              Top Contributors
            </h2>
            <table className="min-w-full text-left border border-gray-700 border-collapse">
              <thead>
                <tr className="bg-gray-700">
                  <th className="py-2 px-4 border-b border-gray-600">Username</th>
                  <th className="py-2 px-4 border-b border-gray-600">Posts Count</th>
                </tr>
              </thead>
              <tbody>
                {contributors.length > 0 ? (
                  contributors.map((user, idx) => (
                    <tr key={idx} className="hover:bg-gray-700">
                      <td className="py-2 px-4 border-b border-gray-600">{user.name}</td>
                      <td className="py-2 px-4 border-b border-gray-600">
                        {user.total_shoutouts}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="2" className="py-4 text-center text-gray-400">
                      No data available
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {/* Most Tagged Users */}
          <div className="bg-gray-800 p-6 rounded-2xl shadow-lg">
            <h2 className="text-2xl font-semibold mb-4 text-blue-300">
              Most Tagged Users
            </h2>
            <table className="min-w-full text-left border border-gray-700 border-collapse">
              <thead>
                <tr className="bg-gray-700">
                  <th className="py-2 px-4 border-b border-gray-600">Username</th>
                  <th className="py-2 px-4 border-b border-gray-600">Times Tagged</th>
                </tr>
              </thead>
              <tbody>
                {tags.length > 0 ? (
                  tags.map((tag, idx) => (
                    <tr key={idx} className="hover:bg-gray-700">
                      <td className="py-2 px-4 border-b border-gray-600">{tag.name}</td>
                      <td className="py-2 px-4 border-b border-gray-600">
                        {tag.times_tagged}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="2" className="py-4 text-center text-gray-400">
                      No data available
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
