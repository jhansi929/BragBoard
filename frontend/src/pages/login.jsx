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
      const res = await loginUser({ email, password });

      if (res && res.data) {
        let { access_token, refresh_token, role } = res.data;

        // ✅ Normalize role strictly
        role = role?.toLowerCase().trim() === "admin" ? "admin" : "employee";

        // Store tokens and role
        localStorage.setItem("access_token", access_token);
        localStorage.setItem("refresh_token", refresh_token);
        localStorage.setItem("user_role", role);

        console.log("Logged in role:", role); // ✅ Debug

        setMessage("✅ Login successful! Redirecting...");

        // Redirect based on role
        setTimeout(() => {
          if (role === "admin") {
            navigate("/admin", { replace: true });
          } else {
            navigate("/dashboard", { replace: true });
          }
        }, 500);
      } else {
        setMessage("❌ Invalid response from server");
      }
    } catch (error) {
      console.error(error);
      setMessage(error.response?.data?.detail || "❌ Login failed");
    }
  };

  return (
    <div className="flex items-center justify-center h-screen w-screen bg-gray-900">
      <div className="bg-gray-800 text-white p-8 sm:p-10 rounded-2xl shadow-2xl w-full max-w-md">
        <h1 className="text-4xl font-extrabold text-blue-400 text-center mb-6 tracking-wide">
          BragBoard
        </h1>
        <h2 className="text-2xl font-semibold text-center mb-6 text-gray-100">
          Login to Continue
        </h2>

        <form onSubmit={handleLogin}>
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
          <button
            type="submit"
            className="w-full bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-xl font-semibold transition-all duration-200"
          >
            Login
          </button>

          {message && (
            <p className="mt-4 text-red-400 text-center text-sm font-medium">
              {message}
            </p>
          )}
        </form>

        <p className="mt-6 text-gray-400 text-center">
          Don’t have an account?{" "}
          <span
            onClick={() => navigate("/register")}
            className="text-blue-400 hover:underline cursor-pointer font-semibold"
          >
            Register here
          </span>
        </p>
      </div>
    </div>
  );
}
