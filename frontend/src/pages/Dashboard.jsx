import { useState, useEffect, useContext } from 'react';
import api from '../api';
import AuthContext from '../context/AuthContext';
import Navbar from '../components/Navbar';
import { useToast } from '../context/ToastContext';

function Dashboard() {
    const { user } = useContext(AuthContext);
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [showCompleted, setShowCompleted] = useState(false);

    const [teams, setTeams] = useState([]);
    const [selectedTask, setSelectedTask] = useState(null);
    const [subtaskTitle, setSubtaskTitle] = useState('');
    const [taskHistory, setTaskHistory] = useState([]);

    // New Task State
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [priority, setPriority] = useState('medium');
    const [assigneeId, setAssigneeId] = useState('');
    const [deadline, setDeadline] = useState('');
    const [teamId, setTeamId] = useState('');
    const { addToast } = useToast();

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
                priority,
                deadline: deadline || null,
                user_id: assigneeId ? parseInt(assigneeId) : null,
                team_id: teamId ? parseInt(teamId) : (user?.role === 'manager' && user?.team_id ? user.team_id : null)
            };
            await api.post('/tasks/', payload);
            addToast("Task Created", `Successfully created task: ${title}`);
            setShowModal(false);
            await fetchTasks(); // Wait for fetch before modal closes for smoother feel
            setTitle('');
            setDescription('');
            setPriority('medium');
            setAssigneeId('');
            setDeadline('');
            setTeamId('');
        } catch (error) {
            console.error(error);
            addToast("Error", "Failed to create task");
        }
    };

    const handleSubtaskCreate = async (e) => {
        e.preventDefault();
        if (!subtaskTitle.trim()) {
            alert("Please enter a subtask title");
            return;
        }
        try {
            await api.post(`/tasks/${selectedTask.id}/subtasks`, { title: subtaskTitle });
            setSubtaskTitle('');
            refreshSelectedTask();
            fetchTasks(); // Refresh main list too for progress bars
        } catch (err) {
            alert(err.response?.data?.detail || "Failed to add subtask");
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
        const response = await api.get('/tasks/');
        setTasks(response.data);
        const updated = response.data.find(t => t.id === selectedTask.id);
        setSelectedTask(updated);
    };

    // Fetch history when a task is selected
    useEffect(() => {
        if (!selectedTask) {
            setTaskHistory([]);
            return;
        }

        const fetchTaskHistory = async () => {
            try {
                const res = await api.get(`/tasks/${selectedTask.id}/history`);
                setTaskHistory(res.data);
            } catch (err) {
                console.error('Failed to fetch task history', err);
                setTaskHistory([]);
            }
        };

        fetchTaskHistory();
    }, [selectedTask]);

    const isManager = user?.role === 'admin' || user?.role === 'manager';

    return (
        <div className="dashboard-container">
            <Navbar />

            <div className="content">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                        <h2 style={{ fontSize: '2rem', margin: 0, background: 'linear-gradient(to right, white, #a1a1aa)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>My Tasks</h2>
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
                    {isManager && (
                        <button onClick={() => setShowModal(true)} className="create-btn">
                            + New Task
                        </button>
                    )}
                </div>

                {loading ? <p style={{ color: 'var(--text-secondary)' }}>Loading tasks...</p> : (
                    <div className="task-grid">
                        {tasks.filter(t => showCompleted || t.status.toLowerCase() !== 'completed').map(task => {
                            const totalSub = task.subtasks ? task.subtasks.length : 0;
                            const completedSub = task.subtasks ? task.subtasks.filter(s => s.is_completed).length : 0;
                            const progress = totalSub === 0 ? 0 : Math.round((completedSub / totalSub) * 100);

                            return (
                                <div key={task.id} className="task-card" onClick={() => setSelectedTask(task)} style={{ cursor: 'pointer' }}>
                                    <div>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '10px' }}>
                                            <h3 style={{ fontSize: '1.2rem', margin: 0 }}>{task.title}</h3>
                                            <div style={{ display: 'flex', gap: '5px' }}>
                                                {task.priority && <span className={`priority-badge priority-${task.priority.toLowerCase()}`}>{task.priority}</span>}
                                                <span className={`status-badge ${task.status.toLowerCase().replace(' ', '-')}`}>{task.status}</span>
                                            </div>
                                        </div>
                                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '15px' }}>{task.description || 'No description provided.'}</p>
                                        {task.deadline && (
                                            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '10px' }}>
                                                📅 {new Date(task.deadline).toLocaleString()}
                                            </div>
                                        )}
                                    </div>

                                    {totalSub > 0 && (
                                        <div style={{ marginTop: 'auto' }}>
                                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8em', marginBottom: '6px', color: 'var(--text-secondary)' }}>
                                                <span>Progress</span>
                                                <span>{progress}%</span>
                                            </div>
                                            <div style={{ width: '100%', background: 'rgba(255,255,255,0.1)', height: '6px', borderRadius: '3px', overflow: 'hidden' }}>
                                                <div style={{ width: `${progress}%`, background: 'var(--primary)', height: '100%', borderRadius: '3px', transition: 'all 0.4s ease' }}></div>
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
                        <form onSubmit={handleCreateTask} style={{ display: 'grid', gap: '15px' }}>
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
                                style={{ minHeight: '100px', resize: 'vertical' }}
                            />
                            <select
                                value={priority}
                                onChange={e => setPriority(e.target.value)}
                            >
                                <option value="low">Low Priority</option>
                                <option value="medium">Medium Priority</option>
                                <option value="high">High Priority</option>
                            </select>
                            <input
                                type="datetime-local"
                                value={deadline || ''}
                                onChange={e => setDeadline(e.target.value)}
                            />
                            <input
                                type="number"
                                placeholder="Assign to User ID (Optional)"
                                value={assigneeId}
                                onChange={e => setAssigneeId(e.target.value)}
                            />
                            {user?.role === 'admin' && (
                                <select
                                    value={teamId}
                                    onChange={e => setTeamId(e.target.value)}
                                >
                                    <option value="">Select Team (Optional)</option>
                                    {teams.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
                                </select>
                            )}
                            <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
                                <button type="button" onClick={() => setShowModal(false)} className="cancel-btn" style={{ flex: 1 }}>Cancel</button>
                                <button type="submit" className="submit-btn" style={{ flex: 1 }}>Create Card</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {selectedTask && (
                <div className="modal-overlay">
                    <div className="modal" style={{ maxWidth: '600px', width: '90%' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '25px', paddingBottom: '15px', borderBottom: '1px solid var(--glass-border)' }}>
                            <input
                                value={selectedTask.title}
                                onChange={(e) => handleUpdateTaskDetails({ title: e.target.value })}
                                style={{ fontSize: '1.5em', background: 'transparent', border: 'none', color: 'white', fontWeight: 'bold', width: '80%', padding: 0 }}
                            />
                            <button onClick={() => setSelectedTask(null)} style={{ background: 'transparent', color: 'var(--text-secondary)', fontSize: '1.5rem', padding: '0 5px' }}>×</button>
                        </div>

                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '25px' }}>
                            <div>
                                <label style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '8px', display: 'block' }}>Status</label>
                                <div style={{ display: 'flex', gap: '5px', marginBottom: '20px', background: 'rgba(255,255,255,0.05)', padding: '4px', borderRadius: '8px' }}>
                                    {['Open', 'In Progress', 'Completed'].map(status => (
                                        <button
                                            key={status}
                                            onClick={() => handleUpdateTaskDetails({ status })}
                                            style={{
                                                flex: 1,
                                                background: selectedTask.status === status ? 'var(--primary)' : 'transparent',
                                                color: selectedTask.status === status ? 'white' : 'var(--text-secondary)',
                                                border: 'none',
                                                padding: '8px',
                                                borderRadius: '6px',
                                                cursor: 'pointer',
                                                fontSize: '0.8rem',
                                                transition: 'all 0.2s',
                                                fontWeight: selectedTask.status === status ? 'bold' : 'normal'
                                            }}
                                        >
                                            {status}
                                        </button>
                                    ))}
                                </div>

                                <label style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '8px', display: 'block' }}>Priority</label>
                                <div style={{ display: 'flex', gap: '5px', marginBottom: '20px', background: 'rgba(255,255,255,0.05)', padding: '4px', borderRadius: '8px' }}>
                                    {['low', 'medium', 'high'].map(prio => (
                                        <button
                                            key={prio}
                                            onClick={() => handleUpdateTaskDetails({ priority: prio })}
                                            style={{
                                                flex: 1,
                                                background: selectedTask.priority === prio ? ({ low: 'var(--success)', medium: 'var(--warning)', high: 'var(--danger)' }[prio]) : 'transparent',
                                                color: selectedTask.priority === prio ? 'white' : 'var(--text-secondary)',
                                                border: 'none',
                                                padding: '8px',
                                                borderRadius: '6px',
                                                cursor: 'pointer',
                                                fontSize: '0.8rem',
                                                textTransform: 'capitalize',
                                                opacity: selectedTask.priority === prio ? 1 : 0.7,
                                                transition: 'all 0.2s',
                                                fontWeight: selectedTask.priority === prio ? 'bold' : 'normal',
                                                boxShadow: selectedTask.priority === prio ? '0 2px 10px rgba(0,0,0,0.2)' : 'none'
                                            }}
                                        >
                                            {prio}
                                        </button>
                                    ))}
                                </div>
                            </div>
                            {isManager && (
                                <div>
                                    <label style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '5px', display: 'block' }}>Assigned Team</label>
                                    <select
                                        value={selectedTask.team_id || ''}
                                        onChange={(e) => handleUpdateTaskDetails({ team_id: parseInt(e.target.value) })}
                                    >
                                        <option value="">Unassigned</option>
                                        {teams.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
                                    </select>
                                </div>
                            )}
                        </div>

                        <div style={{ marginBottom: '30px' }}>
                            <label style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '5px', display: 'block' }}>Description</label>
                            <textarea
                                value={selectedTask.description || ''}
                                onChange={(e) => handleUpdateTaskDetails({ description: e.target.value })}
                                placeholder="Add a description..."
                                style={{ width: '100%', minHeight: '100px', resize: 'vertical' }}
                            />
                        </div>

                        <h4 style={{ marginBottom: '15px', color: 'var(--text-secondary)', textTransform: 'uppercase', fontSize: '0.85rem', letterSpacing: '1px' }}>Subtasks</h4>
                        <div style={{ marginBottom: '20px', display: 'grid', gap: '8px' }}>
                            {selectedTask.subtasks && selectedTask.subtasks.map(sub => (
                                <div key={sub.id} style={{ display: 'flex', alignItems: 'center', padding: '12px', background: 'rgba(255,255,255,0.03)', borderRadius: '8px', transition: 'background 0.2s' }}>
                                    <input
                                        type="checkbox"
                                        checked={sub.is_completed}
                                        onChange={() => handleSubtaskToggle(sub.id, sub.is_completed, sub.title)}
                                        style={{ width: '18px', height: '18px', marginRight: '15px', accentColor: 'var(--primary)' }}
                                    />
                                    <span style={{ textDecoration: sub.is_completed ? 'line-through' : 'none', color: sub.is_completed ? 'var(--text-secondary)' : 'white', flex: 1 }}>{sub.title}</span>
                                    <button onClick={() => handleSubtaskDelete(sub.id)} style={{ background: 'transparent', color: 'var(--danger)', padding: '5px', opacity: 0.7 }}>
                                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                                    </button>
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
                            <button type="submit" className="primary-btn" style={{ padding: '0.75rem 1.5rem' }}>Add</button>
                        </form>

                        <div style={{ marginTop: '20px' }}>
                            <h4 style={{ marginBottom: '12px', color: 'var(--text-secondary)', textTransform: 'uppercase', fontSize: '0.85rem', letterSpacing: '1px' }}>History</h4>
                            {taskHistory.length === 0 ? (
                                <p style={{ color: 'var(--text-secondary)' }}>No history available for this task.</p>
                            ) : (
                                <div style={{ display: 'grid', gap: '10px' }}>
                                    {taskHistory.map(h => (
                                        <div key={h.id} style={{ padding: '10px', background: 'rgba(255,255,255,0.02)', borderRadius: '8px', fontSize: '0.9rem' }}>
                                            <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                                                <div>{h.action}{h.field_changed ? ` — ${h.field_changed}` : ''}</div>
                                                <div>{new Date(h.timestamp).toLocaleString()}</div>
                                            </div>
                                            <div style={{ color: 'white' }}>
                                                <strong>{h.user?.username || 'Unknown'}</strong>
                                                {h.old_value || h.new_value ? (
                                                    <span style={{ marginLeft: '8px', color: 'var(--text-secondary)' }}>: {h.old_value || ''} → {h.new_value || ''}</span>
                                                ) : null}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default Dashboard;
