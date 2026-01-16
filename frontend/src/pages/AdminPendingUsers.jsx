import { useState, useEffect, useContext } from 'react';
import api from '../api';
import AuthContext from '../context/AuthContext';
import Navbar from '../components/Navbar';

function AdminPendingUsers() {
    const [users, setUsers] = useState([]);
    const [error, setError] = useState('');
    const { token } = useContext(AuthContext);

    useEffect(() => {
        fetchPendingUsers();
    }, []);

    const fetchPendingUsers = async () => {
        try {
            const response = await api.get('/admin/pending-users');
            setUsers(response.data);
        } catch (err) {
            setError(err.message);
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

    return (
        <div className="dashboard-container">
            <Navbar />
            <div className="content">
                <h2>Pending User Approvals</h2>
                {error && <p style={{ color: 'var(--danger)' }}>{error}</p>}

                <div className="card" style={{ marginTop: '20px', padding: 0, overflow: 'hidden' }}>
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
            </div>
        </div>
    );
}

export default AdminPendingUsers;
