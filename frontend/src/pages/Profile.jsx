import React, { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import axios from "axios";

export default function Profile() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUserProfile = async () => {
      try {
        const token = localStorage.getItem("access_token"); // stored after login
        if (!token) {
          console.error("No token found — user not logged in.");
          setLoading(false);
          return;
        }

        const response = await axios.get("http://127.0.0.1:8000/me", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        setUser(response.data);
      } catch (error) {
        console.error("Error fetching user profile:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchUserProfile();
  }, []);

  if (loading) {
    return (
      <div className="flex h-screen w-screen items-center justify-center text-white bg-gray-900">
        <p>Loading profile...</p>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="flex h-screen w-screen items-center justify-center text-white bg-gray-900">
        <p>Unable to load user data. Please log in again.</p>
      </div>
    );
  }

  return (
    <div className="flex h-screen w-screen bg-gray-900 text-white overflow-hidden">
      <Sidebar />
      <div className="flex-1 p-10 overflow-y-auto ml-64">
        <h1 className="text-3xl font-bold mb-6 text-blue-400">Your Profile</h1>

        <div className="bg-gray-800 p-6 rounded-2xl shadow-lg max-w-md">
          <p><span className="font-semibold">Name:</span> {user.name}</p>
          <p><span className="font-semibold">Email:</span> {user.email}</p>
          <p><span className="font-semibold">Department:</span> {user.department || "—"}</p>
          <p><span className="font-semibold">Role:</span> {user.role || "User"}</p>
          <p>
            <span className="font-semibold">Joined:</span>{" "}
            {user.joined_at
              ? new Date(user.joined_at).toLocaleDateString()
              : "Not available"}
          </p>
        </div>
      </div>
    </div>
  );
}
