// src/App.jsx
import { useState } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Register from "./pages/register";
import Login from "./pages/login";


function App() {
  const [token, setToken] = useState(localStorage.getItem("access_token"));

  return (
    <Routes>
      <Route
        path="/"
        element={token ? <Navigate to="/dashboard" /> : <Navigate to="/login" />}
      />
      <Route
        path="/login"
        element={token ? <Navigate to="/dashboard" /> : <Login setToken={setToken} />}
      />
      <Route
        path="/register"
        element={token ? <Navigate to="/dashboard" /> : <Register />}
      />
      <Route
        path="/dashboard"
        element={
          token ? (
            <div className="text-center mt-8">
              <h2 className="text-2xl">Welcome to BragBoard!</h2>
            </div>
          ) : (
            <Navigate to="/login" />
          )
        }
      />
    </Routes>
  );
}

export default App;
