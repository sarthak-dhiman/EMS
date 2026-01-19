import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import Navbar from '../components/Navbar';

function AdminTeams() {
    const navigate = useNavigate();
    const [teams, setTeams] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        fetchTeams();
    }, []);

    const fetchTeams = async () => {
        try {
            const res = await api.get('/teams/');
            setTeams(res.data);
        } catch (error) {
            console.error("Failed to fetch teams", error);
        }
    };

    const deleteTeam = async (id) => {
        if (!confirm('Are you sure you want to delete this team?')) return;
        try {
            await api.delete(`/teams/${id}`);
            fetchTeams();
        } catch (err) {
            alert("Failed to delete team");
        }
    };

    const filteredTeams = teams.filter(team =>
        team.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        team.members?.some(m => m.username.toLowerCase().includes(searchTerm.toLowerCase()))
    );

    return (
        <div className="dashboard-container">
            <Navbar />
            <div className="content">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
                    <h2 style={{ fontSize: '2rem', margin: 0, background: 'linear-gradient(to right, white, #a1a1aa)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>Team Management</h2>
                    <button onClick={() => navigate('/admin/teams/create')} className="create-btn">
                        + New Team
                    </button>
                </div>

                <div style={{ marginBottom: '30px' }}>
                    <input
                        type="text"
                        placeholder="Search teams by name or member..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        style={{ width: '100%', padding: '12px', background: 'rgba(255,255,255,0.05)', border: '1px solid var(--glass-border)', borderRadius: '8px', color: 'white' }}
                    />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
                    {filteredTeams.map(team => (
                        <div key={team.id} className="task-card" onClick={() => navigate(`/admin/teams/${team.id}`)} style={{ cursor: 'pointer', borderLeft: '4px solid var(--primary)' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                                <h3>{team.name}</h3>
                                <button onClick={(e) => { e.stopPropagation(); deleteTeam(team.id); }} style={{ background: 'transparent', color: 'var(--danger)', padding: 0, opacity: 0.6 }}>
                                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                                </button>
                            </div>

                            <div style={{ marginTop: 'auto' }}>
                                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Manager: <span style={{ color: 'white' }}>{team.manager ? team.manager.username : 'Unassigned'}</span></p>
                                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '5px' }}>{team.members?.length || 0} Members</p>
                            </div>
                        </div>
                    ))}
                </div>

            </div>
        </div>
    );
}

export default AdminTeams;
