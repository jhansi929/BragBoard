import React, { useState, useEffect } from "react";

const CreateShoutout = ({ token }) => {
  const [message, setMessage] = useState("");
  const [department, setDepartment] = useState("");
  const [shoutouts, setShoutouts] = useState([]);
  const [loading, setLoading] = useState(false);

  // Example department list (you can adjust this)
  const departments = ["IT", "HR", "Finance", "Marketing", "Operations"];

  // Fetch shoutouts
  useEffect(() => {
    fetch("http://127.0.0.1:8000/shoutouts", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then((res) => res.json())
      .then((data) => setShoutouts(data))
      .catch((err) => console.error("Error fetching shoutouts:", err));
  }, [token]);

  // Handle form submit
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!message.trim()) return alert("Please enter a message");

    setLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/shoutouts", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          message,
          department: department || null, // Send department if selected
        }),
      });

      if (res.ok) {
        const newShoutout = await res.json();
        setShoutouts((prev) => [newShoutout, ...prev]); // instantly add new shoutout
        setMessage("");
        setDepartment("");
      } else {
        console.error("Failed to create shoutout:", await res.text());
      }
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white shadow-lg rounded-xl mt-8">
      <h2 className="text-2xl font-bold mb-4 text-center">Create a Shoutout 🎉</h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <textarea
          className="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
          rows="3"
          placeholder="Write your appreciation message..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
        ></textarea>

        <div>
          <label className="block font-semibold mb-2">Choose Department (optional)</label>
          <select
            className="w-full p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
            value={department}
            onChange={(e) => setDepartment(e.target.value)}
          >
            <option value="">-- Select Department --</option>
            {departments.map((dept) => (
              <option key={dept} value={dept}>
                {dept}
              </option>
            ))}
          </select>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition duration-300"
        >
          {loading ? "Posting..." : "Post Shoutout 🎉"}
        </button>
      </form>

      <h3 className="text-xl font-semibold mt-8 mb-3 text-center">Recent Shoutouts</h3>
      <div className="space-y-3">
        {shoutouts.length === 0 ? (
          <p className="text-gray-500 text-center">No shoutouts yet.</p>
        ) : (
          shoutouts.map((s) => (
            <div key={s.id} className="p-3 border rounded-lg bg-gray-50 shadow-sm">
              <p className="font-medium">{s.message}</p>
              <p className="text-sm text-gray-500">Sender ID: {s.sender_id}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default CreateShoutout;
