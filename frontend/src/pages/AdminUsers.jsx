import { useState, useEffect, useContext } from 'react';
import api from '../api';
import Navbar from '../components/Navbar';
import AuthContext from '../context/AuthContext';

function AdminUsers() {
    const [users, setUsers] = useState([]);
    const [search, setSearch] = useState('');
    const [filterRole, setFilterRole] = useState('all');
    const { token } = useContext(AuthContext);

    useEffect(() => {
        fetchUsers();
    }, [search, filterRole]);

    const fetchUsers = async () => {
        try {
            // Build query params
            const params = new URLSearchParams();
            if (search) params.append('search', search);
            if (filterRole !== 'all') params.append('role', filterRole);

            const res = await api.get(`/admin/users?${params.toString()}`);
            setUsers(res.data);
        } catch (error) {
            console.error("Failed to fetch users", error);
        }
    };

    const [showCreateModal, setShowCreateModal] = useState(false);
    const [newUser, setNewUser] = useState({ username: '', email: '', password: '', role: 'employee' });

    const handleCreateUser = async (e) => {
        e.preventDefault();
        try {
            await api.post('/admin/users', newUser);
            setShowCreateModal(false);
            setNewUser({ username: '', email: '', password: '', role: 'employee' });
            fetchUsers();
        } catch (error) {
            alert("Failed to create user: " + (error.response?.data?.detail || error.message));
        }
    };

    const handleDelete = async (userId) => {
        if (!confirm('Are you sure you want to delete this user?')) return;
        try {
            await api.delete(`/auth/${userId}`);
            fetchUsers();
        } catch (error) {
            alert("Failed to delete user: " + (error.response?.data?.detail || error.message));
        }
    };

    return (
        <div className="dashboard-container">
            <Navbar />
            <div className="content">
                <h2>User Management</h2>

                <div style={{ display: 'flex', gap: '20px', marginBottom: '20px' }}>
                    <input
                        type="text"
                        placeholder="Search by name or email..."
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                        style={{ flex: 1, marginBottom: 0 }}
                    />
                    <select
                        value={filterRole}
                        onChange={e => setFilterRole(e.target.value)}
                        style={{ width: '200px', marginBottom: 0 }}
                    >
                        <option value="all">All Roles</option>
                        <option value="admin">Admin</option>
                        <option value="manager">Manager</option>
                        <option value="employee">Employee</option>
                    </select>
                    <button onClick={() => setShowCreateModal(true)} className="create-btn" style={{ marginLeft: 'auto' }}>
                        + Create User
                    </button>
                </div>

                {showCreateModal && (
                    <div className="modal-overlay">
                        <div className="modal">
                            <h3>Create New User</h3>
                            <form onSubmit={handleCreateUser}>
                                <input
                                    placeholder="Username"
                                    value={newUser.username}
                                    onChange={e => setNewUser({ ...newUser, username: e.target.value })}
                                    required
                                />
                                <input
                                    type="email"
                                    placeholder="Email"
                                    value={newUser.email}
                                    onChange={e => setNewUser({ ...newUser, email: e.target.value })}
                                    required
                                />
                                <input
                                    type="password"
                                    placeholder="Password"
                                    value={newUser.password}
                                    onChange={e => setNewUser({ ...newUser, password: e.target.value })}
                                    required
                                />
                                <select
                                    value={newUser.role}
                                    onChange={e => setNewUser({ ...newUser, role: e.target.value })}
                                >
                                    <option value="employee">Employee</option>
                                    <option value="manager">Manager</option>
                                    <option value="admin">Admin</option>
                                </select>
                                <div className="modal-actions">
                                    <button type="button" onClick={() => setShowCreateModal(false)} className="cancel-btn">Cancel</button>
                                    <button type="submit" className="submit-btn">Create</button>
                                </div>
                            </form>
                        </div>
                    </div>
                )}

                <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', color: '#fff' }}>
                        <thead>
                            <tr style={{ background: '#333', textAlign: 'left' }}>
                                <th style={{ padding: '15px' }}>ID</th>
                                <th style={{ padding: '15px' }}>Username</th>
                                <th style={{ padding: '15px' }}>Email</th>
                                <th style={{ padding: '15px' }}>Role</th>
                                <th style={{ padding: '15px' }}>Team</th>
                                <th style={{ padding: '15px' }}>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {users.map(user => (
                                <tr key={user.id} style={{ borderBottom: '1px solid #333' }}>
                                    <td style={{ padding: '15px' }}>{user.id}</td>
                                    <td style={{ padding: '15px' }}>{user.username}</td>
                                    <td style={{ padding: '15px' }}>{user.email}</td>
                                    <td style={{ padding: '15px' }}>
                                        <span className={`priority ${user.role === 'admin' ? 'high' :
                                            user.role === 'manager' ? 'medium' : 'low'
                                            }`}>
                                            {user.role}
                                        </span>
                                    </td>
                                    <td style={{ padding: '15px' }}>{user.team_name || '-'}</td>
                                    <td style={{ padding: '15px' }}>
                                        <button
                                            onClick={() => handleDelete(user.id)}
                                            className="delete-btn"
                                            style={{ padding: '5px 10px', fontSize: '0.8em' }}
                                        >
                                            Delete
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}

export default AdminUsers;
