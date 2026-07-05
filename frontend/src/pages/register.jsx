import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { registerUser } from "../api/auth";

export default function Register() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [department, setDepartment] = useState("");
  const [role, setRole] = useState("employee"); // default employee
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    setMessage("Registering...");

    try {
      const res = await registerUser({ name, email, password, department, role });

      if (res && res.data) {
        setMessage("✅ Registration successful! Redirecting to login...");
        setTimeout(() => navigate("/login"), 1000);
      } else {
        setMessage("❌ Invalid response from server");
      }
    } catch (error) {
      console.error(error);
      setMessage(error.response?.data?.detail || "❌ Registration failed");
    }
  };

  return (
    <div className="flex items-center justify-center h-screen w-screen bg-gray-900">
      <div className="bg-gray-800 text-white p-8 sm:p-10 rounded-2xl shadow-2xl w-full max-w-md">
        <h1 className="text-4xl font-extrabold text-blue-400 text-center mb-6 tracking-wide">
          BragBoard
        </h1>
        <h2 className="text-2xl font-semibold text-center mb-6 text-gray-100">
          Create an Account
        </h2>

        <form onSubmit={handleRegister}>
          <input
            type="text"
            placeholder="Full Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="border border-gray-700 bg-gray-900 text-gray-200 p-3 rounded-xl w-full mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />

          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="border border-gray-700 bg-gray-900 text-gray-200 p-3 rounded-xl w-full mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="border border-gray-700 bg-gray-900 text-gray-200 p-3 rounded-xl w-full mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />

          {/* Department Dropdown */}
          <select
            value={department}
            onChange={(e) => setDepartment(e.target.value)}
            className="border border-gray-700 bg-gray-900 text-gray-200 p-3 rounded-xl w-full mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          >
            <option value="">Select Department</option>
            <option value="All">All</option>
            <option value="HR">HR</option>
            <option value="IT">IT</option>
            <option value="Finance">Finance</option>
            <option value="Marketing">Marketing</option>
            <option value="Operations">Operations</option>
          </select>

          {/* Role Selection */}
          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            className="border border-gray-700 bg-gray-900 text-gray-200 p-3 rounded-xl w-full mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          >
            <option value="employee">Employee</option>
            <option value="admin">Admin</option>
          </select>

          <button
            type="submit"
            className="w-full bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-xl font-semibold transition-all duration-200"
          >
            Register
          </button>

          {message && (
            <p className="mt-4 text-red-400 text-center text-sm font-medium">
              {message}
            </p>
          )}
        </form>

        <p className="mt-6 text-gray-400 text-center">
          Already have an account?{" "}
          <span
            onClick={() => navigate("/login")}
            className="text-blue-400 hover:underline cursor-pointer font-semibold"
          >
            Login here
          </span>
        </p>
      </div>
    </div>
  );
}
