import { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import Navbar from '../components/Navbar';

function CreateTeam() {
    const navigate = useNavigate();
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await api.post('/teams/', { name, description });
            navigate('/admin/teams');
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
                        <button onClick={() => navigate('/admin/teams')} className="cancel-btn">Back</button>
                        <h2>Create New Team</h2>
                    </div>

                    <div className="card">
                        <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '20px' }}>
                            {error && <div style={{ color: 'var(--danger)' }}>{error}</div>}

                            <div>
                                <label style={{ display: 'block', marginBottom: '5px' }}>Team Name</label>
                                <input
                                    type="text"
                                    value={name}
                                    onChange={e => setName(e.target.value)}
                                    required
                                    style={{ width: '100%', padding: '10px' }}
                                />
                            </div>

                            <div>
                                <label style={{ display: 'block', marginBottom: '5px' }}>Description (Optional)</label>
                                <textarea
                                    value={description}
                                    onChange={e => setDescription(e.target.value)}
                                    style={{ width: '100%', padding: '10px', minHeight: '100px' }}
                                />
                            </div>

                            <button type="submit" className="primary-btn" style={{ padding: '12px' }}>Create Team</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default CreateTeam;
