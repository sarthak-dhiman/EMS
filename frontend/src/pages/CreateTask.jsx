import { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import Navbar from '../components/Navbar';
import AuthContext from '../context/AuthContext';

function CreateTask() {
    const navigate = useNavigate();
    const { user } = useContext(AuthContext);
    const [formData, setFormData] = useState({
        title: '',
        description: '',
        priority: 'medium',
        deadline: '',
        team_id: '',
        user_id: ''
    });
    const [teams, setTeams] = useState([]);
    const [teamMembers, setTeamMembers] = useState([]);
    const [error, setError] = useState('');

    useEffect(() => {
        if (!user) return;
        if (user.role === 'admin') {
            fetchTeams();
        } else if (user.role === 'manager') {
            // Manager: fetch their own team to get ID and Members
            fetchMyTeam();
        }
    }, [user]);

    // When team_id changes, fetch members (if admin)
    useEffect(() => {
        if (!user) return;
        if (user.role === 'admin' && formData.team_id) {
            const team = teams.find(t => t.id === parseInt(formData.team_id));
            setTeamMembers(team ? team.members : []);
        }
    }, [formData.team_id, teams, user]);

    const fetchTeams = async () => {
        try {
            const res = await api.get('/teams/');
            setTeams(res.data);
            if (res.data.length > 0) {
                // default to first team? No, let them choose.
            }
        } catch (err) {
            console.error(err);
        }
    };

    const fetchMyTeam = async () => {
        try {
            const res = await api.get('/teams/my-team');
            setFormData(prev => ({ ...prev, team_id: res.data.id }));
            setTeamMembers(res.data.members || []);
        } catch (err) {
            setError("Could not load team info");
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await api.post('/tasks/', {
                title: formData.title,
                description: formData.description,
                priority: formData.priority,
                deadline: formData.deadline || null,
                team_id: parseInt(formData.team_id),
                user_id: formData.user_id ? parseInt(formData.user_id) : null
            });
            // Redirect based on role? Or just back to dashboard
            if (user.role === 'admin') navigate('/admin/teams'); // Or where? Admin doesn't have a "Task Board" yet?
            else navigate('/team-dashboard');
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
                        <button onClick={() => navigate(-1)} className="cancel-btn">Back</button>
                        <h2>Create New Task</h2>
                    </div>

                    <div className="card">
                        <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '20px' }}>
                            {error && <div style={{ color: 'var(--danger)' }}>{error}</div>}

                            <div>
                                <label style={{ display: 'block', marginBottom: '5px' }}>Title</label>
                                <input
                                    value={formData.title}
                                    onChange={e => setFormData({ ...formData, title: e.target.value })}
                                    required
                                    style={{ width: '100%', padding: '10px' }}
                                />
                            </div>

                            <div>
                                <label style={{ display: 'block', marginBottom: '5px' }}>Description</label>
                                <textarea
                                    value={formData.description}
                                    onChange={e => setFormData({ ...formData, description: e.target.value })}
                                    style={{ width: '100%', padding: '10px', minHeight: '100px' }}
                                />
                            </div>

                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                                <div>
                                    <label style={{ display: 'block', marginBottom: '5px' }}>Priority</label>
                                    <select
                                        value={formData.priority}
                                        onChange={e => setFormData({ ...formData, priority: e.target.value })}
                                        style={{ width: '100%', padding: '10px' }}
                                    >
                                        <option value="low">Low</option>
                                        <option value="medium">Medium</option>
                                        <option value="high">High</option>
                                    </select>
                                </div>
                                <div>
                                    <label style={{ display: 'block', marginBottom: '5px' }}>Deadline</label>
                                    <input
                                        type="datetime-local"
                                        value={formData.deadline}
                                        onChange={e => setFormData({ ...formData, deadline: e.target.value })}
                                        style={{ width: '100%', padding: '10px' }}
                                    />
                                </div>
                            </div>

                            {user?.role === 'admin' && (
                                <div>
                                    <label style={{ display: 'block', marginBottom: '5px' }}>Team</label>
                                    <select
                                        value={formData.team_id}
                                        onChange={e => setFormData({ ...formData, team_id: e.target.value, user_id: '' })}
                                        required
                                        style={{ width: '100%', padding: '10px' }}
                                    >
                                        <option value="">Select Team...</option>
                                        {teams.map(t => (
                                            <option key={t.id} value={t.id}>{t.name}</option>
                                        ))}
                                    </select>
                                </div>
                            )}

                            <div>
                                <label style={{ display: 'block', marginBottom: '5px' }}>Assign To</label>
                                <select
                                    value={formData.user_id}
                                    onChange={e => setFormData({ ...formData, user_id: e.target.value })}
                                    style={{ width: '100%', padding: '10px' }}
                                    disabled={!formData.team_id}
                                >
                                    <option value="">Unassigned (Team Task)</option>
                                    {teamMembers.map(m => (
                                        <option key={m.id} value={m.id}>{m.username}</option>
                                    ))}
                                </select>
                            </div>

                            <button type="submit" className="primary-btn" style={{ padding: '12px' }}>Create Task</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default CreateTask;
