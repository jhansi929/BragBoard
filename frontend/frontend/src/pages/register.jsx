
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { registerUser } from "../api/auth";

export default function Register() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [department, setDepartment] = useState("");
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    setMessage("Registering...");
    try {
      await registerUser({ name, email, password, department });
      setMessage("Registration successful! Redirecting to login...");
      setTimeout(() => navigate("/login"), 1500);
    } catch (error) {
      console.error(error);
      setMessage(error.response?.data?.detail || "Registration failed");
    }
  };

  return (
    <div className="flex items-center justify-center h-screen w-screen bg-gradient-to-r from-green-400 to-blue-500">
      <form
        onSubmit={handleRegister}
        className="bg-white p-10 sm:p-12 rounded-2xl shadow-2xl w-full max-w-md text-center"
      >
        <h2 className="text-3xl font-bold mb-6 text-gray-800">Register</h2>

        <input
          type="text"
          placeholder="Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="border p-3 rounded w-full mb-4 focus:outline-none focus:ring-2 focus:ring-green-400"
          required
        />

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="border p-3 rounded w-full mb-4 focus:outline-none focus:ring-2 focus:ring-green-400"
          required
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="border p-3 rounded w-full mb-4 focus:outline-none focus:ring-2 focus:ring-green-400"
          required
        />

        {/* Department Dropdown */}
        <select
          value={department}
          onChange={(e) => setDepartment(e.target.value)}
          className="border p-3 rounded w-full mb-4 focus:outline-none focus:ring-2 focus:ring-green-400"
          required
        >
          <option value="">-- Select Department --</option>
          <option value="IT">IT</option>
          <option value="HR">HR</option>
          <option value="Finance">Finance</option>
          <option value="Marketing">Marketing</option>
          <option value="Operations">Operations</option>
        </select>

        <button
          type="submit"
          className="w-full bg-green-500 text-white p-3 rounded-xl hover:bg-green-600 transition-colors"
        >
          Register
        </button>

        {message && <p className="mt-4 text-red-500 text-center">{message}</p>}
      </form>
    </div>
  );
}
