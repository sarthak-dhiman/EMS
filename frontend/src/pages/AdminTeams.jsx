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
            // Backend expects list of IDs
            await api.put(`/teams/${selectedTeam.id}/members`, [parseInt(selectedUserToAdd)]);
            const updatedTeam = await api.get(`/teams/${selectedTeam.id}`); // Re-fetch to get updated members?
            // Or easier, just re-fetch all teams and update selectedTeam from that list locally if possible, 
            // but teams list might not have full member details if not joinedloaded. 
            // We added joinedload to get_all_teams, so fetching teams again is fine.
            fetchTeams();
            setSelectedTeam(prev => ({
                ...prev,
                members: [...(prev.members || []), users.find(u => u.id === parseInt(selectedUserToAdd))]
            }));
            // Actually better to just refresh the whole team object from list
            // But let's just re-fetch teams and find the updated one
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

    return (
        <div className="dashboard-container">
            <Navbar />
            <div className="content">
                <h2>Team Management</h2>
                {error && <p style={{ color: 'red' }}>{error}</p>}

                <form onSubmit={createTeam} style={{ marginBottom: '20px' }}>
                    <input
                        type="text"
                        placeholder="Team Name"
                        value={newTeamName}
                        onChange={e => setNewTeamName(e.target.value)}
                        required
                    />
                    <button type="submit">Create Team</button>
                </form>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
                    {teams.map(team => (
                        <div key={team.id} className="card" style={{ padding: '15px', background: '#222', cursor: 'pointer' }} onClick={() => setSelectedTeam(team)}>
                            <h3>{team.name}</h3>
                            <p>Manager ID: {team.manager_id || 'None'}</p>
                            <p>{team.members?.length || 0} Members</p>
                            <button onClick={(e) => { e.stopPropagation(); deleteTeam(team.id); }} style={{ background: 'red' }}>Delete Team</button>
                        </div>
                    ))}
                </div>

                {selectedTeam && (
                    <div className="modal-overlay">
                        <div className="modal" style={{ maxWidth: '600px' }}>
                            <h3>Manage Team: {selectedTeam.name}</h3>

                            <div style={{ marginBottom: '20px' }}>
                                <h4>Add Member</h4>
                                <div style={{ display: 'flex', gap: '10px' }}>
                                    <select value={selectedUserToAdd} onChange={e => setSelectedUserToAdd(e.target.value)}>
                                        <option value="">Select User...</option>
                                        {users.filter(u => u.role === 'employee' && u.team_name !== selectedTeam.name).map(u => (
                                            <option key={u.id} value={u.id}>{u.username} ({u.team_name || 'No Team'})</option>
                                        ))}
                                    </select>
                                    <button onClick={addMember}>Add</button>
                                </div>
                            </div>

                            <h4>Current Members</h4>
                            <ul style={{ listStyle: 'none', padding: 0 }}>
                                {selectedTeam.members && selectedTeam.members.map(member => (
                                    <li key={member.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '10px', background: '#333', marginBottom: '5px' }}>
                                        <span>{member.username} ({member.email})</span>
                                        <button onClick={() => removeMember(member.id)} className="delete-btn" style={{ fontSize: '0.8em' }}>Remove</button>
                                    </li>
                                ))}
                            </ul>

                            <button onClick={() => setSelectedTeam(null)} className="cancel-btn" style={{ marginTop: '20px' }}>Close</button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default AdminTeams;
