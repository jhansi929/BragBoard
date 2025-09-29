import { useState } from "react";

export default function Login({ setToken }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch("http://127.0.0.1:8000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      // inside handleLogin after successful login
        if (response.status === 200) {
            const data = await response.json();
            localStorage.setItem("access_token", data.access_token);
            if (typeof setToken === "function") setToken(data.access_token);
                setMessage("Login successful!");
            }else {
        const data = await response.json();
        setMessage(data.detail || "Login failed");
      }
    } catch (error) {
      setMessage("Error connecting to server");
    }
  };

  return (
    <div className="flex justify-center items-center h-screen bg-gray-100">
      <form
        onSubmit={handleLogin}
        className="bg-white p-8 rounded shadow-md w-96"
      >
        <h2 className="text-2xl font-bold mb-6">Login</h2>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="border p-2 rounded w-full mb-4"
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="border p-2 rounded w-full mb-4"
          required
        />
        <button
          type="submit"
          className="bg-green-500 text-white p-2 rounded w-full"
        >
          Login
        </button>
        {message && <p className="mt-4 text-red-500">{message}</p>}
      </form>
    </div>
  );
}
