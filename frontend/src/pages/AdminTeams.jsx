import { useState, useEffect, useContext } from 'react';
import api from '../api';
import AuthContext from '../context/AuthContext';
import Navbar from '../components/Navbar';

function AdminTeams() {
    const [teams, setTeams] = useState([]);
    const [users, setUsers] = useState([]);
    const [newTeamName, setNewTeamName] = useState('');
    const [error, setError] = useState('');
    const [selectedTeam, setSelectedTeam] = useState(null);
    const [selectedUserToAdd, setSelectedUserToAdd] = useState('');
    const { token } = useContext(AuthContext);

    const [showCreateModal, setShowCreateModal] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        fetchTeams();
        fetchUsers();
    }, []);

    const fetchTeams = async () => {
        try {
            const res = await api.get('/teams/');
            setTeams(res.data);
        } catch (error) {
            console.error("Failed to fetch teams", error);
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

    const createTeam = async (e) => {
        e.preventDefault();
        try {
            await api.post('/teams/', { name: newTeamName });
            setNewTeamName('');
            setShowCreateModal(false);
            fetchTeams();
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
        }
    };

    const deleteTeam = async (id) => {
        if (!confirm('Are you sure?')) return;
        try {
            await api.delete(`/teams/${id}`);
            fetchTeams();
            if (selectedTeam?.id === id) setSelectedTeam(null);
        } catch (err) {
            alert("Failed to delete team");
        }
    };

    const addMember = async () => {
        if (!selectedUserToAdd) return;
        try {
            await api.put(`/teams/${selectedTeam.id}/members`, [parseInt(selectedUserToAdd)]);
            fetchTeams();
            const res = await api.get('/teams/');
            setTeams(res.data);
            setSelectedTeam(res.data.find(t => t.id === selectedTeam.id));
            setSelectedUserToAdd('');
        } catch (err) {
            alert("Failed to add member: " + (err.response?.data?.detail || err.message));
        }
    };

    const removeMember = async (userId) => {
        if (!confirm('Remove user from team?')) return;
        try {
            await api.delete(`/teams/${selectedTeam.id}/members/${userId}`);
            const res = await api.get('/teams/');
            setTeams(res.data);
            setSelectedTeam(res.data.find(t => t.id === selectedTeam.id));
        } catch (err) {
            alert("Failed to remove member");
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
                    <button onClick={() => setShowCreateModal(true)} className="create-btn">
                        + New Team
                    </button>
                </div>

                {error && <p style={{ color: 'var(--danger)', marginBottom: '1rem' }}>{error}</p>}

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
                        <div key={team.id} className="task-card" onClick={() => setSelectedTeam(team)} style={{ cursor: 'pointer', borderLeft: '4px solid var(--primary)' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                                <h3>{team.name}</h3>
                                <button onClick={(e) => { e.stopPropagation(); deleteTeam(team.id); }} style={{ background: 'transparent', color: 'var(--danger)', padding: 0, opacity: 0.6 }}>
                                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                                </button>
                            </div>

                            <div style={{ marginTop: 'auto' }}>
                                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Manager ID: <span style={{ color: 'white' }}>{team.manager_id || 'Unassigned'}</span></p>
                                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '5px' }}>{team.members?.length || 0} Members</p>
                            </div>
                        </div>
                    ))}
                </div>

                {showCreateModal && (
                    <div className="modal-overlay">
                        <div className="modal">
                            <h3>Create New Team</h3>
                            <form onSubmit={createTeam} style={{ display: 'grid', gap: '15px' }}>
                                <input
                                    type="text"
                                    placeholder="Team Name"
                                    value={newTeamName}
                                    onChange={e => setNewTeamName(e.target.value)}
                                    required
                                />
                                <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
                                    <button type="button" onClick={() => setShowCreateModal(false)} className="cancel-btn" style={{ flex: 1 }}>Cancel</button>
                                    <button type="submit" className="submit-btn" style={{ flex: 1 }}>Create</button>
                                </div>
                            </form>
                        </div>
                    </div>
                )}

                {selectedTeam && (
                    <div className="modal-overlay">
                        <div className="modal" style={{ maxWidth: '600px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                                <h3>{selectedTeam.name}</h3>
                                <button onClick={() => setSelectedTeam(null)} className="cancel-btn" style={{ padding: '5px 10px' }}>Close</button>
                            </div>

                            <div style={{ marginBottom: '30px', padding: '20px', background: 'rgba(255,255,255,0.02)', borderRadius: '12px' }}>
                                <h4 style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '10px', textTransform: 'uppercase' }}>Add Member</h4>
                                <div style={{ display: 'flex', gap: '10px' }}>
                                    <select value={selectedUserToAdd} onChange={e => setSelectedUserToAdd(e.target.value)}>
                                        <option value="">Select User...</option>
                                        {users.filter(u => u.role === 'employee' && u.team_name !== selectedTeam.name).map(u => (
                                            <option key={u.id} value={u.id}>{u.username} ({u.team_name || 'No Team'})</option>
                                        ))}
                                    </select>
                                    <button onClick={addMember} className="primary-btn" style={{ padding: '10px 20px' }}>Add</button>
                                </div>
                            </div>

                            <h4 style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '15px', textTransform: 'uppercase' }}>Current Members</h4>
                            <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
                                {selectedTeam.members && selectedTeam.members.length > 0 ? (
                                    <ul style={{ listStyle: 'none', padding: 0 }}>
                                        {selectedTeam.members.map(member => (
                                            <li key={member.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px', background: 'var(--glass-bg)', marginBottom: '8px', borderRadius: '8px', border: '1px solid var(--glass-border)' }}>
                                                <span>{member.username} <span style={{ color: 'var(--text-secondary)', fontSize: '0.85em' }}>({member.email})</span></span>
                                                <button onClick={() => removeMember(member.id)} style={{ color: 'var(--danger)', background: 'transparent', padding: '5px' }}>Remove</button>
                                            </li>
                                        ))}
                                    </ul>
                                ) : (
                                    <p style={{ color: 'var(--text-secondary)', fontStyle: 'italic' }}>No members assigned yet.</p>
                                )}
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default AdminTeams;
