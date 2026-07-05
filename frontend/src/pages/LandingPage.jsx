// src/pages/LandingPage.jsx
import { useNavigate } from "react-router-dom";

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col h-screen w-screen bg-gradient-to-r from-green-400 to-blue-500">
      {/* Header / Brand */}
      <header className="text-white text-5xl font-bold p-8 text-center shadow-lg">
        BragBoard
      </header>

      {/* Center content */}
      <div className="flex flex-1 items-center justify-center">
        <div className="bg-white p-10 sm:p-12 rounded-2xl shadow-2xl w-full max-w-md text-center">
          <h2 className="text-3xl font-bold mb-4 text-gray-800">Welcome to BragBoard</h2>
          <p className="text-gray-600 mb-6">
            Recognize and celebrate your teammates’ achievements.
          </p>

          <button
            onClick={() => navigate("/register")}
            className="w-full mb-4 bg-green-500 text-white p-3 rounded-xl hover:bg-green-600 transition-colors"
          >
            Register
          </button>

          <button
            onClick={() => navigate("/login")}
            className="w-full bg-blue-500 text-white p-3 rounded-xl hover:bg-blue-600 transition-colors"
          >
            Login
          </button>
        </div>
      </div>
    </div>
  );
}
