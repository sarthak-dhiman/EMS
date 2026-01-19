import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { useContext } from 'react';
import { AuthProvider } from './context/AuthContext';
import AuthContext from './context/AuthContext';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import AdminUsers from './pages/AdminUsers';
import AdminPendingUsers from './pages/AdminPendingUsers';
import AdminTeams from './pages/AdminTeams';
import TeamDashboard from './pages/TeamDashboard';
import CreateTeam from './pages/CreateTeam';
import TeamDetail from './pages/TeamDetail';
import CreateUser from './pages/CreateUser';
import CreateTask from './pages/CreateTask';
import ForgotPassword from './pages/ForgotPassword';
import Profile from './pages/Profile';
import './App.css';

const PrivateRoute = ({ roles = [] }) => {
  const { user, loading } = useContext(AuthContext);

  if (loading) return <div>Loading...</div>;

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (roles.length > 0 && !roles.includes(user.role)) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
};

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />

          {/* Protected Routes */}
          <Route element={<PrivateRoute />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/profile" element={<Profile />} />
          </Route>

          <Route element={<PrivateRoute roles={['admin']} />}>
            <Route path="/users" element={<AdminUsers />} />
            <Route path="/admin/users/create" element={<CreateUser />} />
            <Route path="/admin/pending-users" element={<AdminPendingUsers />} />
            <Route path="/admin/teams" element={<AdminTeams />} />
            <Route path="/admin/teams/create" element={<CreateTeam />} />
            <Route path="/admin/teams/:id" element={<TeamDetail />} />
          </Route>

          <Route element={<PrivateRoute roles={['manager', 'admin']} />}>
            <Route path="/tasks/create" element={<CreateTask />} />
            <Route path="/team-dashboard" element={<TeamDashboard />} />
          </Route>

          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;