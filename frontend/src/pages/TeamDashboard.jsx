import { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import AuthContext from '../context/AuthContext';
import Navbar from '../components/Navbar';

function TeamDashboard() {
    const navigate = useNavigate();
    const [team, setTeam] = useState(null);
    const [showCompleted, setShowCompleted] = useState(false);
    const { user } = useContext(AuthContext);

    useEffect(() => {
        fetchMyTeam();
    }, []);

    const fetchMyTeam = async () => {
        try {
            const res = await api.get('/teams/my-team');
            setTeam(res.data);
        } catch (error) {
            console.error(error);
        }
    };

    if (!team) return <div>Loading Team...</div>;

    return (
        <div className="dashboard-container">
            <Navbar />
            <div className="content">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
                    <div>
                        <h2 style={{ fontSize: '2rem', margin: 0 }}>Team: {team.name}</h2>
                        <p style={{ color: 'var(--text-secondary)' }}>{team.description}</p>
                    </div>
                    {/* Only Manager/Admin can create task. User role is checked in AuthContext/Route but good to check here too */}
                    {(user.role === 'manager' || user.role === 'admin') && (
                        <button onClick={() => navigate('/tasks/create')} className="create-btn">
                            + Assign Task
                        </button>
                    )}
                </div>

                <div className="card" style={{ marginBottom: '20px' }}>
                    <h3>Team Members</h3>
                    <div style={{ marginTop: '20px', display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '20px' }}>
                        {team.members && team.members.map(member => (
                            <div key={member.id} style={{ padding: '15px', background: 'var(--bg-dark)', borderRadius: '8px', border: '1px solid var(--glass-border)' }}>
                                <div style={{ fontWeight: 'bold' }}>{member.username}</div>
                                <div style={{ fontSize: '0.8em', color: 'var(--text-secondary)' }}>{member.email}</div>
                            </div>
                        ))}
                    </div>
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
                                .filter(task => showCompleted || task.status !== 'completed')
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

export default TeamDashboard;
