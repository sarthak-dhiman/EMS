import { useState, useEffect, useContext } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api';
import Navbar from '../components/Navbar';
import AuthContext from '../context/AuthContext';

function TeamDetail() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [team, setTeam] = useState(null);
    const [users, setUsers] = useState([]);
    const [selectedUserToAdd, setSelectedUserToAdd] = useState('');
    const [selectedManager, setSelectedManager] = useState('');
    const [loading, setLoading] = useState(true);
    const [showCompleted, setShowCompleted] = useState(false);

    useEffect(() => {
        fetchTeam();
        fetchUsers();
    }, [id]);

    const fetchTeam = async () => {
        try {
            const res = await api.get(`/teams/${id}`);
            setTeam(res.data);
            if (res.data.manager_id) setSelectedManager(res.data.manager_id);
        } catch (error) {
            console.error(error);
            if (error.response && error.response.status === 404) {
                alert("Team not found");
                navigate('/admin/teams');
            }
        } finally {
            setLoading(false);
        }
    };

    const fetchUsers = async () => {
        try {
            const res = await api.get('/admin/users');
            setUsers(res.data);
        } catch (error) {
            console.error("Failed to fetch users", error);
        }
    };

    const handleAssignManager = async () => {
        if (!selectedManager) return;
        try {
            await api.put(`/teams/${id}/manager?manager_id=${selectedManager}`);
            alert("Manager assigned successfully");
            fetchTeam();
        } catch (err) {
            alert("Failed to assign manager: " + (err.response?.data?.detail || err.message));
        }
    };

    const addMember = async () => {
        if (!selectedUserToAdd) return;
        try {
            await api.put(`/teams/${id}/members`, [parseInt(selectedUserToAdd)]);
            fetchTeam();
            setSelectedUserToAdd('');
        } catch (err) {
            alert("Failed to add member: " + (err.response?.data?.detail || err.message));
        }
    };

    const removeMember = async (memberId) => {
        if (team.manager_id === memberId) {
            alert("Cannot remove the Team Manager. Please assign a new manager first.");
            return;
        }
        if (!confirm('Remove user from team?')) return;
        try {
            await api.delete(`/teams/${id}/members/${memberId}`);
            fetchTeam();
        } catch (err) {
            alert("Failed to remove member: " + (err.response?.data?.detail || err.message));
        }
    };

    if (loading) return <div>Loading...</div>;
    if (!team) return <div>Team not found</div>;

    return (
        <div className="dashboard-container">
            <Navbar />
            <div className="content">
                <div style={{ display: 'flex', alignItems: 'center', gap: '20px', marginBottom: '30px' }}>
                    <button onClick={() => navigate('/admin/teams')} className="cancel-btn">Back</button>
                    <h2>{team.name}</h2>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px', marginBottom: '30px' }}>
                    <div className="card">
                        <h3>Team Management</h3>
                        <div style={{ marginTop: '20px' }}>
                            <label style={{ display: 'block', color: 'var(--text-secondary)', marginBottom: '8px' }}>Assign Manager</label>
                            <div style={{ display: 'flex', gap: '10px' }}>
                                <select
                                    value={selectedManager}
                                    onChange={e => setSelectedManager(e.target.value)}
                                    style={{ padding: '10px', flex: 1, color: 'white', background: 'var(--bg-dark)', border: '1px solid var(--glass-border)', borderRadius: '6px' }}
                                >
                                    <option value="" style={{ color: 'black' }}>Select Manager...</option>
                                    {users.map(u => (
                                        <option key={u.id} value={u.id} style={{ color: 'black' }}>{u.username} ({u.role})</option>
                                    ))}
                                </select>
                                <button onClick={handleAssignManager} className="primary-btn">Update</button>
                            </div>
                            {team.manager && (
                                <p style={{ marginTop: '10px', fontSize: '0.9rem', color: 'var(--success)' }}>
                                    Current Manager: <strong>{team.manager.username}</strong>
                                </p>
                            )}
                        </div>
                    </div>

                    <div className="card">
                        <h3>Add Members</h3>
                        <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
                            <select
                                value={selectedUserToAdd}
                                onChange={e => setSelectedUserToAdd(e.target.value)}
                                style={{ padding: '10px', flex: 1, color: 'white', background: 'var(--bg-dark)', border: '1px solid var(--glass-border)', borderRadius: '6px' }}
                            >
                                <option value="" style={{ color: 'black' }}>Select User to Add...</option>
                                {users.filter(u => u.team_name !== team.name).map(u => (
                                    <option key={u.id} value={u.id} style={{ color: 'black' }}>{u.username} ({u.role})</option>
                                ))}
                            </select>
                            <button onClick={addMember} className="primary-btn">Add</button>
                        </div>
                    </div>
                </div>

                <div className="card" style={{ marginBottom: '30px' }}>
                    <h3>Current Members ({team.members?.length || 0})</h3>
                    {team.members && team.members.length > 0 ? (
                        <div style={{ marginTop: '20px', display: 'grid', gap: '10px', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))' }}>
                            {team.members.map(member => (
                                <div key={member.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '15px', background: 'var(--bg-dark)', borderRadius: '8px', border: member.id === team.manager_id ? '1px solid var(--primary)' : 'none' }}>
                                    <div>
                                        <div style={{ fontWeight: 'bold' }}>{member.username} {member.id === team.manager_id && <span style={{ fontSize: '0.7em', background: 'var(--primary)', padding: '2px 6px', borderRadius: '4px', marginLeft: '6px' }}>MANAGER</span>}</div>
                                        <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{member.email}</div>
                                    </div>
                                    <button onClick={() => removeMember(member.id)} className="delete-btn" style={{ padding: '4px 10px', fontSize: '0.8rem' }}>Remove</button>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p style={{ color: 'var(--text-secondary)', marginTop: '20px' }}>No members in this team.</p>
                    )}
                </div>

                <div className="card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <h3>Team Tasks</h3>
                        <div style={{ display: 'flex', background: 'rgba(255,255,255,0.05)', borderRadius: '6px', padding: '2px' }}>
                            <button
                                onClick={() => setShowCompleted(false)}
                                style={{
                                    background: !showCompleted ? 'rgba(255,255,255,0.1)' : 'transparent',
                                    color: !showCompleted ? 'white' : 'var(--text-secondary)',
                                    border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer', fontSize: '0.85rem'
                                }}
                            >
                                Active
                            </button>
                            <button
                                onClick={() => setShowCompleted(true)}
                                style={{
                                    background: showCompleted ? 'rgba(255,255,255,0.1)' : 'transparent',
                                    color: showCompleted ? 'white' : 'var(--text-secondary)',
                                    border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer', fontSize: '0.85rem'
                                }}
                            >
                                All
                            </button>
                        </div>
                    </div>

                    {team.tasks && team.tasks.length > 0 ? (
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px', marginTop: '20px' }}>
                            {team.tasks
                                .filter(task => showCompleted || task.status.toLowerCase() !== 'completed')
                                .map(task => {
                                    const assignee = team.members ? team.members.find(m => m.id === task.user_id) : null;
                                    return (
                                        <div key={task.id} className="task-card" style={{ borderLeft: `4px solid ${task.priority === 'high' ? 'var(--danger)' : task.priority === 'medium' ? 'var(--warning)' : 'var(--success)'}`, opacity: task.status === 'completed' ? 0.6 : 1 }}>
                                            <h4>{task.title}</h4>
                                            <p style={{ fontSize: '0.9em', color: 'var(--text-secondary)', marginBottom: '10px' }}>{task.description}</p>

                                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85em', color: 'var(--text-secondary)' }}>
                                                <span>Assignee: <span style={{ color: 'white' }}>{assignee ? assignee.username : 'Unassigned'}</span></span>
                                                <span>Status: <span style={{ color: 'white', textTransform: 'capitalize' }}>{task.status}</span></span>
                                            </div>
                                            {task.deadline && (
                                                <div style={{ marginTop: '5px', fontSize: '0.85em', color: 'var(--text-secondary)' }}>
                                                    Deadline: <span style={{ color: 'white' }}>{new Date(task.deadline).toLocaleDateString()}</span>
                                                </div>
                                            )}
                                        </div>
                                    );
                                })}
                        </div>
                    ) : (
                        <p style={{ color: 'var(--text-secondary)', marginTop: '20px' }}>No tasks assigned to this team yet.</p>
                    )}
                </div>
            </div>
        </div>
    );
}

export default TeamDetail;
