import { useState, useEffect, useContext } from 'react';
import api from '../api';
import AuthContext from '../context/AuthContext';
import Navbar from '../components/Navbar';

function AdminPendingUsers() {
    const [users, setUsers] = useState([]);
    const [passwordResets, setPasswordResets] = useState([]);
    const [error, setError] = useState('');
    const { token } = useContext(AuthContext);

    useEffect(() => {
        fetchPendingUsers();
        fetchPasswordResets();
    }, []);

    const fetchPendingUsers = async () => {
        try {
            const response = await api.get('/admin/pending-users');
            setUsers(response.data);
        } catch (err) {
            setError(err.message);
        }
    };

    const fetchPasswordResets = async () => {
        try {
            const res = await api.get('/admin/password-resets');
            setPasswordResets(res.data);
        } catch (err) {
            console.error("Failed to fetch password resets", err);
        }
    };

    const approveUser = async (userId) => {
        try {
            await api.put(`/admin/approve-user/${userId}`);
            // Remove user from list
            setUsers(users.filter(user => user.id !== userId));
        } catch (err) {
            alert(err.message);
        }
    };

    const handleResetPassword = async (requestId) => {
        try {
            const res = await api.post(`/admin/password-resets/${requestId}/reset`);
            alert(`Password Reset Successful.\n\nTemporary Password: ${res.data.temp_password}\n\nPlease share this with the user.`);
            setPasswordResets(passwordResets.filter(r => r.id !== requestId));
        } catch (err) {
            alert(err.response?.data?.detail || "Failed to reset password");
        }
    };

    return (
        <div className="dashboard-container">
            <Navbar />
            <div className="content">
                <h2>Pending User Approvals</h2>
                {error && <p style={{ color: 'var(--danger)' }}>{error}</p>}

                <div className="card" style={{ marginTop: '20px', padding: 0, overflow: 'hidden' }}>
                    <div style={{ padding: '20px', borderBottom: '1px solid var(--glass-border)' }}>
                        <h3 style={{ margin: 0 }}>Registration Requests</h3>
                    </div>
                    {users.length === 0 ? <p style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)' }}>No pending approvals.</p> : (
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Username</th>
                                    <th>Email</th>
                                    <th>Role</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {users.map(user => (
                                    <tr key={user.id}>
                                        <td>{user.id}</td>
                                        <td>{user.username}</td>
                                        <td>{user.email}</td>
                                        <td>
                                            <span className="status-badge open">{user.role}</span>
                                        </td>
                                        <td>
                                            <button
                                                onClick={() => approveUser(user.id)}
                                                style={{ background: 'rgba(16, 185, 129, 0.2)', color: '#34d399', border: '1px solid rgba(16, 185, 129, 0.3)', padding: '6px 14px', borderRadius: '6px' }}
                                            >
                                                Approve
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>

                <div className="card" style={{ marginTop: '40px', padding: 0, overflow: 'hidden' }}>
                    <div style={{ padding: '20px', borderBottom: '1px solid var(--glass-border)' }}>
                        <h3 style={{ margin: 0 }}>Password Reset Requests</h3>
                    </div>
                    {passwordResets.length === 0 ? <p style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)' }}>No pending password resets.</p> : (
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>User ID</th>
                                    <th>Email</th>
                                    <th>Requested At</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {passwordResets.map(req => (
                                    <tr key={req.id}>
                                        <td>{req.id}</td>
                                        <td>{req.user_id}</td>
                                        <td>{req.email}</td>
                                        <td>{new Date(req.created_at).toLocaleString()}</td>
                                        <td>
                                            <button
                                                onClick={() => handleResetPassword(req.id)}
                                                style={{ background: 'rgba(59, 130, 246, 0.2)', color: '#60a5fa', border: '1px solid rgba(59, 130, 246, 0.3)', padding: '6px 14px', borderRadius: '6px' }}
                                            >
                                                Reset & Show Temp Pass
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>
        </div>
    );
}

export default AdminPendingUsers;
