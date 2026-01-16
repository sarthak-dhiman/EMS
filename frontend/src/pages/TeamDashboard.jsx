import { useState, useEffect, useContext } from 'react';
import api from '../api';
import AuthContext from '../context/AuthContext';

function TeamDashboard() {
    const [team, setTeam] = useState(null);
    const [tasks, setTasks] = useState([]);
    const [newTask, setNewTask] = useState({ title: '', description: '', user_id: '' });
    const { token, user } = useContext(AuthContext);

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

    const createTask = async (e) => {
        e.preventDefault();
        try {
            await api.post('/tasks/', {
                title: newTask.title,
                description: newTask.description,
                user_id: newTask.user_id ? parseInt(newTask.user_id) : null,
                team_id: team.id
            });
            alert('Task assigned!');
            setNewTask({ title: '', description: '', user_id: '' });
        } catch (err) {
            alert(err.response?.data?.detail || err.message);
        }
    };

    if (!team) return <div>Loading Team...</div>;

    return (
        <div style={{ padding: '20px' }}>
            <h2>Team: {team.name}</h2>
            <p>{team.description}</p>

            <div style={{ marginTop: '20px' }}>
                <h3>Assign Task</h3>
                <form onSubmit={createTask} style={{ maxWidth: '400px' }}>
                    <div style={{ marginBottom: '10px' }}>
                        <input
                            type="text"
                            placeholder="Task Title"
                            value={newTask.title}
                            onChange={e => setNewTask({ ...newTask, title: e.target.value })}
                            required
                            style={{ width: '100%', padding: '8px' }}
                        />
                    </div>
                    <div style={{ marginBottom: '10px' }}>
                        <textarea
                            placeholder="Description"
                            value={newTask.description}
                            onChange={e => setNewTask({ ...newTask, description: e.target.value })}
                            style={{ width: '100%', padding: '8px' }}
                        />
                    </div>
                    <div style={{ marginBottom: '10px' }}>
                        <select
                            value={newTask.user_id}
                            onChange={e => setNewTask({ ...newTask, user_id: e.target.value })}
                            style={{ width: '100%', padding: '8px' }}
                        >
                            <option value="">Assign to whole team</option>
                            {/* We need members list here. TeamResponse has members list if we set up backend right 
                                In schema TeamResponse, members: List[UserResponse] = []
                                But we need the relationship loaded. 
                                Let's assume members are returned.
                            */}
                            {team.members && team.members.map(member => (
                                <option key={member.id} value={member.id}>{member.username}</option>
                            ))}
                        </select>
                    </div>
                    <button type="submit">Assign Task</button>
                </form>
            </div>
        </div>
    );
}

export default TeamDashboard;
