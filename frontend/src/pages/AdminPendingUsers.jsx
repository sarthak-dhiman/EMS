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
                {error && <p style={{ color: 'red' }}>{error}</p>}
                {users.length === 0 ? <p>No pending approvals.</p> : (
                    <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '20px', background: '#333', color: '#fff' }}>
                        <thead>
                            <tr style={{ textAlign: 'left', borderBottom: '1px solid #555' }}>
                                <th style={{ padding: '10px' }}>ID</th>
                                <th style={{ padding: '10px' }}>Username</th>
                                <th style={{ padding: '10px' }}>Email</th>
                                <th style={{ padding: '10px' }}>Role</th>
                                <th style={{ padding: '10px' }}>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {users.map(user => (
                                <tr key={user.id} style={{ borderBottom: '1px solid #444' }}>
                                    <td style={{ padding: '10px' }}>{user.id}</td>
                                    <td style={{ padding: '10px' }}>{user.username}</td>
                                    <td style={{ padding: '10px' }}>{user.email}</td>
                                    <td style={{ padding: '10px' }}>{user.role}</td>
                                    <td style={{ padding: '10px' }}>
                                        <button
                                            onClick={() => approveUser(user.id)}
                                            style={{ background: '#52c41a', color: 'white', border: 'none', padding: '5px 10px', cursor: 'pointer', borderRadius: '4px' }}
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
    );
}

export default AdminPendingUsers;
