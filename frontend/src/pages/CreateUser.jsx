import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import Navbar from '../components/Navbar';

function CreateUser() {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        role: 'employee',
        team_name: '' // Optional
    });
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await api.post('/admin/users', formData);
            navigate('/users');
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
        }
    };

    return (
        <div className="dashboard-container">
            <Navbar />
            <div className="content">
                <div style={{ maxWidth: '600px', margin: '0 auto' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '20px', marginBottom: '30px' }}>
                        <button onClick={() => navigate('/users')} className="cancel-btn">Back</button>
                        <h2>Create New User</h2>
                    </div>

                    <div className="card">
                        <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '20px' }}>
                            {error && <div style={{ color: 'var(--danger)' }}>{error}</div>}

                            <div>
                                <label>Username</label>
                                <input
                                    value={formData.username}
                                    onChange={e => setFormData({ ...formData, username: e.target.value })}
                                    required
                                    style={{ width: '100%', padding: '10px' }}
                                />
                            </div>

                            <div>
                                <label>Email</label>
                                <input
                                    type="email"
                                    value={formData.email}
                                    onChange={e => setFormData({ ...formData, email: e.target.value })}
                                    required
                                    style={{ width: '100%', padding: '10px' }}
                                />
                            </div>

                            <div>
                                <label>Password</label>
                                <input
                                    type="password"
                                    value={formData.password}
                                    onChange={e => setFormData({ ...formData, password: e.target.value })}
                                    required
                                    style={{ width: '100%', padding: '10px' }}
                                />
                            </div>

                            <div>
                                <label>Role</label>
                                <select
                                    value={formData.role}
                                    onChange={e => setFormData({ ...formData, role: e.target.value })}
                                    style={{ width: '100%', padding: '10px' }}
                                >
                                    <option value="employee">Employee</option>
                                    <option value="manager">Manager</option>
                                    <option value="admin">Admin</option>
                                </select>
                            </div>

                            <button type="submit" className="primary-btn" style={{ padding: '12px' }}>Create User</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default CreateUser;
