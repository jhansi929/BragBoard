import { Routes, Route, Navigate } from "react-router-dom";
import LandingPage from "./pages/LandingPage.jsx";
import Login from "./pages/login.jsx";
import Register from "./pages/register.jsx";
import Dashboard from "./pages/dashboard.jsx";
import AdminDashboard from "./pages/AdminDashboard.jsx";
import PostShoutout from "./pages/PostShoutout.jsx";
import ShoutoutFeed from "./pages/ShoutoutFeed.jsx";
import Profile from "./pages/Profile.jsx";
import Settings from "./pages/Settings.jsx"; 
import ReportedShoutouts from "./pages/ReportedShoutouts.jsx";


// Protected route component
function RequireAuth({ children, allowedRoles }) {
  const accessToken = localStorage.getItem("access_token");
  const userRole = (localStorage.getItem("user_role") || "").toLowerCase().trim();

  if (!accessToken) return <Navigate to="/login" replace />;

  if (allowedRoles && !allowedRoles.map(r => r.toLowerCase()).includes(userRole)) {
    return userRole === "admin" ? <Navigate to="/admin" replace /> : <Navigate to="/dashboard" replace />;
  }

  return children;
}

function App() {
  return (
    <div className="min-h-screen w-full bg-gray-900 text-white overflow-x-hidden">
      <Routes>
        {/* Landing page as default route */}
        <Route path="/" element={<LandingPage />} />

        {/* Public pages */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Employee protected routes */}
        <Route
          path="/dashboard"
          element={
            <RequireAuth allowedRoles={["employee"]}>
              <Dashboard />
            </RequireAuth>
          }
        />
        <Route
          path="/postshoutout"
          element={
            <RequireAuth allowedRoles={["employee"]}>
              <PostShoutout />
            </RequireAuth>
          }
        />
        <Route
          path="/shoutouts"
          element={
            <RequireAuth allowedRoles={["employee"]}>
              <ShoutoutFeed />
            </RequireAuth>
          }
        />
        <Route
          path="/profile"
          element={
            <RequireAuth allowedRoles={["employee", "admin"]}>
              <Profile />
            </RequireAuth>
          }
        />
        <Route
          path="/settings"
          element={
            <RequireAuth allowedRoles={["employee", "admin"]}>
              <Settings />
            </RequireAuth>
          }
        />

        {/* Admin protected route */}
        <Route
          path="/admin"
          element={
            <RequireAuth allowedRoles={["admin"]}>
              <AdminDashboard />
            </RequireAuth>
          }
        />
        <Route path="/admin/reports" element={<ReportedShoutouts />} />

        {/* Catch-all redirects to landing page */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
}

export default App;
