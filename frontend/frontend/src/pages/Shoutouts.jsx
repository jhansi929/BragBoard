import { useEffect, useState } from "react";
import axios from "axios";

export default function Shoutouts() {
  const [message, setMessage] = useState("");
  const [department, setDepartment] = useState("");
  const [shoutouts, setShoutouts] = useState([]);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const API_URL = "http://127.0.0.1:8000";
  const token = localStorage.getItem("access_token");
  const config = { headers: { Authorization: `Bearer ${token}` } };

  // Fetch current user
  useEffect(() => {
    if (!token) return;
    axios.get(`${API_URL}/me`, config)
      .then(res => setUser(res.data))
      .catch(err => console.error(err));
  }, [token]);

  // Fetch shoutouts
  useEffect(() => {
    if (!token) return;
    axios.get(`${API_URL}/shoutouts`, config)
      .then(res => setShoutouts(res.data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, [token]);

  const postShoutout = () => {
    if (!message) return alert("Message cannot be empty");

    axios.post(`${API_URL}/shoutouts`,
      { message, department: department || null },
      config
    )
      .then(res => setShoutouts(prev => [res.data, ...prev]))
      .catch(err => console.error(err))
      .finally(() => {
        setMessage("");
        setDepartment("");
      });
  };

  if (loading) return <p className="p-4">Loading...</p>;

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">Welcome to BragBoard 🎉</h1>

      <div className="mb-6">
        <h2 className="text-xl font-semibold mb-2">Create a Shoutout 🎊</h2>
        <textarea
          className="w-full p-2 border rounded mb-2"
          placeholder="Write your appreciation message..."
          value={message}
          onChange={e => setMessage(e.target.value)}
        />
        <select
          className="w-full p-2 border rounded mb-2"
          value={department}
          onChange={e => setDepartment(e.target.value)}
        >
          <option value="">-- Select Department --</option>
          <option value="IT">IT</option>
          <option value="Engineering">Engineering</option>
          <option value="HR">HR</option>
          <option value="Sales">Sales</option>
        </select>
        <button
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          onClick={postShoutout}
        >
          Post Shoutout 🎉
        </button>
      </div>

      <div>
        <h2 className="text-xl font-semibold mb-2">Recent Shoutouts</h2>
        {shoutouts.length === 0 ? (
          <p>No shoutouts yet.</p>
        ) : (
          shoutouts.map(s => (
            <div key={s.id} className="border p-3 rounded mb-2 bg-gray-50">
              <p className="font-medium">{s.message}</p>
              <p className="text-sm text-gray-600">
                {s.sender_name} ({s.sender_role}, {s.sender_department || "N/A"})
                {user && user.id === s.sender_id ? " (You)" : ""}
              </p>
              {s.created_at && (
                <p className="text-sm text-gray-500">
                  Created at: {new Date(s.created_at).toLocaleString()}
                </p>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
