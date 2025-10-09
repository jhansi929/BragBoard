import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { loginUser } from "../api/auth";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setMessage("Logging in...");
    try {
      const response = await loginUser({ email, password });
      localStorage.setItem("access_token", response.data.access_token);
      navigate("/dashboard");
    } catch (error) {
      console.error(error);
      setMessage(error.response?.data?.detail || "Login failed");
    }
  };

  return (
    <div className="flex items-center justify-center h-screen w-screen bg-gradient-to-r from-green-400 to-blue-500">
      <form 
        onSubmit={handleLogin} 
        className="bg-white p-10 sm:p-12 rounded-2xl shadow-2xl w-full max-w-md text-center"
      >
        <h2 className="text-3xl font-bold mb-6 text-gray-800">Login</h2>

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="border p-3 rounded w-full mb-4 focus:outline-none focus:ring-2 focus:ring-blue-400"
          required
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="border p-3 rounded w-full mb-4 focus:outline-none focus:ring-2 focus:ring-blue-400"
          required
        />

        <button
          type="submit"
          className="w-full bg-blue-500 text-white p-3 rounded-xl hover:bg-blue-600 transition-colors"
        >
          Login
        </button>

        {message && <p className="mt-4 text-red-500 text-center">{message}</p>}

        <p className="mt-4 text-gray-600">
          Don’t have an account?{" "}
          <span 
            className="text-green-500 cursor-pointer hover:underline" 
            onClick={() => navigate("/register")}
          >
            Register
          </span>
        </p>
      </form>
    </div>
  );
}
