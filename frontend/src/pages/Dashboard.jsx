import { useState, useEffect, useContext } from 'react';
import api from '../api';
import AuthContext from '../context/AuthContext';
import Navbar from '../components/Navbar';

function Dashboard() {
    const { user } = useContext(AuthContext);
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);

    // New Task State
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [priority, setPriority] = useState('Medium');
    const [assigneeId, setAssigneeId] = useState('');

    useEffect(() => {
        fetchTasks();
    }, []);

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

    const handleCreateTask = async (e) => {
        e.preventDefault();
        try {
            const payload = {
                title,
                description,
                priority,
                user_id: assigneeId ? parseInt(assigneeId) : null
            };
            await api.post('/tasks/', payload);
            setShowModal(false);
            fetchTasks();
            // Reset form
            setTitle('');
            setDescription('');
            setPriority('Medium');
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
                        {tasks.map(task => (
                            <div key={task.id} className="task-card">
                                <div className="task-header">
                                    <h3>{task.title}</h3>
                                    <span className={`priority ${task.priority.toLowerCase()}`}>{task.priority}</span>
                                </div>
                                <p>{task.description}</p>
                                <div className="task-footer">
                                    <span className="status">Status: {task.status}</span>
                                    {task.status !== 'Completed' && (
                                        <button onClick={() => handleComplete(task.id)} className="complete-btn">
                                            Mark Complete
                                        </button>
                                    )}
                                </div>
                            </div>
                        ))}
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
                            <select value={priority} onChange={e => setPriority(e.target.value)}>
                                <option>Low</option>
                                <option>Medium</option>
                                <option>High</option>
                            </select>
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
        </div>
    );
}

export default Dashboard;
