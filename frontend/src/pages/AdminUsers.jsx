import { useState, useEffect, useContext } from 'react';
import api from '../api';
import Navbar from '../components/Navbar';
import AuthContext from '../context/AuthContext';

import { useNavigate } from 'react-router-dom';

function AdminUsers() {
    const navigate = useNavigate();
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
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
                    <h2>User Management</h2>
                    <button onClick={() => navigate('/admin/users/create')} className="create-btn">
                        + Create User
                    </button>
                </div>

                <div style={{ display: 'flex', gap: '20px', marginBottom: '30px' }}>
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
                </div>

                <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Username</th>
                                <th>Email</th>
                                <th>Role</th>
                                <th>Team</th>
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
                                        <span className={`status-badge ${user.role}`}>
                                            {user.role}
                                        </span>
                                    </td>
                                    <td>{user.team_name || '-'}</td>
                                    <td>
                                        <button
                                            onClick={() => handleDelete(user.id)}
                                            style={{ background: 'transparent', color: 'var(--danger)', padding: '5px 8px', fontSize: '0.9em' }}
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
