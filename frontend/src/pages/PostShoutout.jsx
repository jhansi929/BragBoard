import React, { useEffect, useState } from "react";
import axios from "axios";
import Sidebar from "../components/Sidebar";

export default function PostShoutout() {
  const [message, setMessage] = useState("");
  const [recipients, setRecipients] = useState([]);
  const [selectedRecipients, setSelectedRecipients] = useState([]);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [popup, setPopup] = useState({ visible: false, text: "", success: false });
  const [showEmojis, setShowEmojis] = useState(false);

  const emojis = ["👏", "🎉", "❤️", "🔥", "💪", "🌟", "✨", "🙌", "😊", "🏆"];

  useEffect(() => {
    const fetchRecipients = async () => {
      try {
        const token = localStorage.getItem("access_token");
        if (!token) return;
        const res = await axios.get("http://127.0.0.1:8000/users/department", {
          headers: { Authorization: `Bearer ${token}` },
        });
        setRecipients(res.data);
      } catch (err) {
        console.error("Error fetching users:", err);
      }
    };
    fetchRecipients();
  }, []);

  const handleSelect = (id) => {
    setSelectedRecipients((prev) =>
      prev.includes(id) ? prev.filter((r) => r !== id) : [...prev, id]
    );
  };

  const handleEmojiClick = (emoji) => {
    setMessage((prev) => prev + emoji);
    setShowEmojis(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!message.trim()) {
      showPopup("Please enter a message", false);
      return;
    }

    try {
      setLoading(true);
      const token = localStorage.getItem("access_token");
      const formData = new FormData();
      formData.append("message", message);
      formData.append("recipient_ids", JSON.stringify(selectedRecipients));
      if (file) formData.append("file", file);

      await axios.post("http://127.0.0.1:8000/shoutouts", formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "multipart/form-data",
        },
      });

      setMessage("");
      setFile(null);
      setSelectedRecipients([]);
      showPopup("✅ Shoutout posted successfully!", true);
    } catch (err) {
      console.error("❌ Error posting shoutout:", err);
      showPopup("❌ Failed to post shoutout!", false);
    } finally {
      setLoading(false);
    }
  };

  const showPopup = (text, success) => {
    setPopup({ visible: true, text, success });
    setTimeout(() => setPopup({ visible: false, text: "", success: false }), 2500);
  };

  return (
    <div className="flex h-screen w-screen bg-gray-900 text-white overflow-hidden">
      <Sidebar />
      <main className="flex-1 bg-gray-900 overflow-y-auto px-8 py-10">
        <div className="w-full max-w-3xl mx-auto">
          <h1 className="text-3xl font-bold mb-8 text-center text-blue-400">
            📢 Post a Shoutout
          </h1>

          {popup.visible && (
            <div
              className={`fixed top-5 right-5 px-4 py-3 rounded-xl shadow-lg text-white transition ${
                popup.success ? "bg-green-600" : "bg-red-600"
              }`}
            >
              {popup.text}
            </div>
          )}

          <form
            onSubmit={handleSubmit}
            className="bg-gray-800 p-6 rounded-2xl shadow-lg border border-gray-700"
          >
            <div className="relative">
              <textarea
                className="w-full p-3 rounded-xl bg-gray-700 text-white resize-none h-28 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                placeholder="Write your shoutout message... 🎉👏❤️"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
              />
              <button
                type="button"
                onClick={() => setShowEmojis(!showEmojis)}
                className="absolute right-3 bottom-3 text-2xl"
                title="Add Emoji"
              >
                😊
              </button>

              {showEmojis && (
                <div className="absolute right-0 bottom-12 bg-gray-800 border border-gray-600 rounded-xl p-3 grid grid-cols-5 gap-2 shadow-lg">
                  {emojis.map((emoji, index) => (
                    <button
                      key={index}
                      type="button"
                      className="text-2xl hover:scale-110 transition"
                      onClick={() => handleEmojiClick(emoji)}
                    >
                      {emoji}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* File Upload */}
            <div className="mt-4">
              <label className="text-blue-400 font-semibold">Attach Image (optional):</label>
              <input
                type="file"
                accept="image/*"
                className="block mt-2 text-white"
                onChange={(e) => setFile(e.target.files[0])}
              />
            </div>

            <h2 className="mt-6 mb-3 text-lg font-semibold text-blue-400">
              Select Recipients:
            </h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 max-h-48 overflow-y-auto">
              {recipients.map((r) => (
                <label
                  key={r.id}
                  className={`cursor-pointer border rounded-xl px-3 py-2 text-sm flex items-center gap-2 transition ${
                    selectedRecipients.includes(r.id)
                      ? "bg-blue-600 border-blue-400"
                      : "bg-gray-700 border-gray-600 hover:bg-gray-600"
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={selectedRecipients.includes(r.id)}
                    onChange={() => handleSelect(r.id)}
                  />
                  {r.name}
                </label>
              ))}
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-8 bg-blue-600 hover:bg-blue-700 py-3 rounded-xl font-semibold transition disabled:opacity-50"
            >
              {loading ? "Posting..." : "Post Shoutout 🎉"}
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}
