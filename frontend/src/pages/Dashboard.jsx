import { useState, useEffect, useContext } from 'react';
import api from '../api';
import AuthContext from '../context/AuthContext';
import Navbar from '../components/Navbar';

function Dashboard() {
    const { user } = useContext(AuthContext);
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);

    const [teams, setTeams] = useState([]);
    const [selectedTask, setSelectedTask] = useState(null);
    const [subtaskTitle, setSubtaskTitle] = useState('');

    // New Task State
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [assigneeId, setAssigneeId] = useState('');

    useEffect(() => {
        fetchTasks();
        if (user?.role === 'admin' || user?.role === 'manager') {
            fetchTeams();
        }
    }, [user]);

    const fetchTasks = async () => {
        try {
            const response = await api.get('/tasks/');
            setTasks(response.data);
        } catch (error) {
            console.error("Failed to fetch tasks", error);
        } finally {
            setLoading(false);
        }
    };

    const fetchTeams = async () => {
        try {
            const res = await api.get('/teams/');
            setTeams(res.data);
        } catch (error) {
            console.error("Failed to fetch teams", error);
        }
    };

    const handleCreateTask = async (e) => {
        e.preventDefault();
        try {
            const payload = {
                title,
                description,
                user_id: assigneeId ? parseInt(assigneeId) : null
            };
            await api.post('/tasks/', payload);
            setShowModal(false);
            fetchTasks();
            // Reset form
            setTitle('');
            setDescription('');
            setAssigneeId('');
        } catch (error) {
            alert("Failed to create task");
        }
    };

    const handleComplete = async (taskId) => {
        try {
            await api.put(`/tasks/${taskId}/status`, { status: "Completed" });
            fetchTasks();
        } catch (error) {
            alert("Failed to update status");
        }
    };

    const handleSubtaskCreate = async (e) => {
        e.preventDefault();
        try {
            await api.post(`/tasks/${selectedTask.id}/subtasks`, { title: subtaskTitle });
            setSubtaskTitle('');
            refreshSelectedTask();
            fetchTasks(); // Refresh main list too for progress bars
        } catch (err) {
            alert("Failed to add subtask");
        }
    };

    const handleSubtaskToggle = async (subtaskId, currentStatus, title) => {
        try {
            await api.put(`/subtasks/${subtaskId}`, { is_completed: !currentStatus, title: title });
            refreshSelectedTask();
            fetchTasks();
        } catch (err) {
            console.error(err);
        }
    };

    const handleSubtaskDelete = async (subtaskId) => {
        if (!confirm("Delete subtask?")) return;
        try {
            await api.delete(`/subtasks/${subtaskId}`);
            refreshSelectedTask();
            fetchTasks();
        } catch (err) {
            console.error(err);
        }
    };

    const handleUpdateTaskDetails = async (updates) => {
        try {
            await api.put(`/tasks/${selectedTask.id}`, updates);
            refreshSelectedTask();
            fetchTasks();
        } catch (err) {
            alert("Failed to update task");
        }
    };

    const refreshSelectedTask = async () => {
        // optimistically update or re-fetch specific task? 
        // We fetching all tasks anyway, so let's just find it in the new list. 
        // But fetchTasks is async state update.
        // Better to re-fetch single task if we had endpoint, but we don't. 
        // We'll rely on fetchTasks updating the list and we updating selectedTask from it.
        // actually for modal responsiveness, manual re-fetch of list is easier.
        const response = await api.get('/tasks/');
        setTasks(response.data);
        const updated = response.data.find(t => t.id === selectedTask.id);
        setSelectedTask(updated);
    };

    const isManager = user?.role === 'admin' || user?.role === 'manager';

    return (
        <div className="dashboard-container">
            <Navbar />

            <div className="content">
                <div className="header">
                    <h2>My Tasks</h2>
                    {isManager && (
                        <button onClick={() => setShowModal(true)} className="create-btn">
                            + New Task
                        </button>
                    )}
                </div>

                {loading ? <p>Loading...</p> : (
                    <div className="task-grid">
                        {tasks.map(task => {
                            const totalSub = task.subtasks ? task.subtasks.length : 0;
                            const completedSub = task.subtasks ? task.subtasks.filter(s => s.is_completed).length : 0;
                            const progress = totalSub === 0 ? 0 : Math.round((completedSub / totalSub) * 100);

                            return (
                                <div key={task.id} className="task-card" onClick={() => setSelectedTask(task)} style={{ cursor: 'pointer' }}>
                                    <div className="task-header">
                                        <h3>{task.title}</h3>
                                        <span className={`status-badge ${task.status.toLowerCase()}`}>{task.status}</span>
                                    </div>
                                    <p>{task.description}</p>

                                    {totalSub > 0 && (
                                        <div style={{ marginTop: '10px' }}>
                                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8em', marginBottom: '2px' }}>
                                                <span>Progress</span>
                                                <span>{progress}%</span>
                                            </div>
                                            <div style={{ width: '100%', background: '#444', height: '6px', borderRadius: '3px' }}>
                                                <div style={{ width: `${progress}%`, background: '#1890ff', height: '100%', borderRadius: '3px', transition: 'width 0.3s' }}></div>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>

            {showModal && (
                <div className="modal-overlay">
                    <div className="modal">
                        <h3>Create New Task</h3>
                        <form onSubmit={handleCreateTask}>
                            <input
                                placeholder="Title"
                                value={title}
                                onChange={e => setTitle(e.target.value)}
                                required
                            />
                            <textarea
                                placeholder="Description"
                                value={description}
                                onChange={e => setDescription(e.target.value)}
                            />
                            <input
                                type="number"
                                placeholder="Assign to User ID (Optional)"
                                value={assigneeId}
                                onChange={e => setAssigneeId(e.target.value)}
                            />
                            <div className="modal-actions">
                                <button type="button" onClick={() => setShowModal(false)} className="cancel-btn">Cancel</button>
                                <button type="submit" className="submit-btn">Create</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {selectedTask && (
                <div className="modal-overlay">
                    <div className="modal" style={{ maxWidth: '700px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                            <input
                                value={selectedTask.title}
                                onChange={(e) => handleUpdateTaskDetails({ title: e.target.value })}
                                style={{ fontSize: '1.5em', background: 'transparent', border: 'none', color: 'white', fontWeight: 'bold', width: '70%' }}
                            />
                            <button onClick={() => setSelectedTask(null)} style={{ background: 'transparent', color: '#aaa', fontSize: '1.5em' }}>×</button>
                        </div>

                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
                            <div>
                                <label>Status</label>
                                <select
                                    value={selectedTask.status}
                                    onChange={(e) => handleUpdateTaskDetails({ status: e.target.value })}
                                    style={{ width: '100%', marginTop: '5px', padding: '8px', background: '#333', color: 'white' }}
                                >
                                    <option value="Open">Open</option>
                                    <option value="In Progress">In Progress</option>
                                    <option value="Completed">Completed</option>
                                </select>
                            </div>
                            {isManager && (
                                <div>
                                    <label>Assigned Team</label>
                                    <select
                                        value={selectedTask.team_id || ''}
                                        onChange={(e) => handleUpdateTaskDetails({ team_id: parseInt(e.target.value) })}
                                        style={{ width: '100%', marginTop: '5px', padding: '8px', background: '#333', color: 'white' }}
                                    >
                                        <option value="">Unassigned</option>
                                        {teams.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
                                    </select>
                                </div>
                            )}
                        </div>

                        <textarea
                            value={selectedTask.description || ''}
                            onChange={(e) => handleUpdateTaskDetails({ description: e.target.value })}
                            placeholder="Description..."
                            style={{ width: '100%', minHeight: '80px', background: '#333', color: 'white', padding: '10px', marginBottom: '20px' }}
                        />

                        <h4>Subtasks</h4>
                        <div style={{ marginBottom: '15px' }}>
                            {selectedTask.subtasks && selectedTask.subtasks.map(sub => (
                                <div key={sub.id} style={{ display: 'flex', alignItems: 'center', marginBottom: '8px', padding: '8px', background: '#2a2a2a', borderRadius: '4px' }}>
                                    <input
                                        type="checkbox"
                                        checked={sub.is_completed}
                                        onChange={() => handleSubtaskToggle(sub.id, sub.is_completed, sub.title)}
                                        style={{ marginRight: '10px' }}
                                    />
                                    <span style={{ textDecoration: sub.is_completed ? 'line-through' : 'none', flex: 1 }}>{sub.title}</span>
                                    <button onClick={() => handleSubtaskDelete(sub.id)} style={{ background: 'transparent', color: '#ff4d4f', padding: '0 5px' }}>×</button>
                                </div>
                            ))}
                        </div>

                        <form onSubmit={handleSubtaskCreate} style={{ display: 'flex', gap: '10px' }}>
                            <input
                                placeholder="Add new subtask..."
                                value={subtaskTitle}
                                onChange={e => setSubtaskTitle(e.target.value)}
                                style={{ flex: 1 }}
                            />
                            <button type="submit" style={{ padding: '8px 15px' }}>Add</button>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}

export default Dashboard;
