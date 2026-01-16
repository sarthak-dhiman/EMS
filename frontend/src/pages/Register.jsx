import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../api';

function Register() {
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        dob: '',
        mobile_number: ''
    });
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleRegister = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess(false);

        try {
            await api.post('/auth/register', formData);
            setSuccess(true);
            setTimeout(() => navigate('/login'), 2000);
        } catch (err) {
            setError(err.response?.data?.detail || 'Registration failed');
        }
    };

    return (
        <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1rem' }}>
            <div className="card" style={{ width: '100%', maxWidth: '450px', padding: '2.5rem', position: 'relative', overflow: 'hidden' }}>
                <div style={{ position: 'absolute', top: '-50%', left: '-50%', width: '200%', height: '200%', background: 'radial-gradient(circle, rgba(99,102,241,0.1) 0%, transparent 50%)', zIndex: -1 }}></div>

                <h2 style={{ textAlign: 'center', fontSize: '2rem', marginBottom: '0.5rem' }}>Create Account</h2>
                <p style={{ textAlign: 'center', color: 'var(--text-secondary)', marginBottom: '2rem' }}>Join the team today</p>

                {error && <div style={{ background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', padding: '12px', borderRadius: '8px', marginBottom: '20px', textAlign: 'center', fontSize: '0.9rem' }}>{error}</div>}

                {success && <div style={{ background: 'rgba(16, 185, 129, 0.1)', color: '#10b981', padding: '12px', borderRadius: '8px', marginBottom: '20px', textAlign: 'center', fontSize: '0.9rem' }}>
                    Registration successful! Redirecting...
                </div>}

                <form onSubmit={handleRegister} style={{ display: 'grid', gap: '15px' }}>
                    <div>
                        <input type="text" name="username" placeholder="Username" value={formData.username} onChange={handleChange} required />
                    </div>
                    <div>
                        <input type="email" name="email" placeholder="Email Address" value={formData.email} onChange={handleChange} required />
                    </div>
                    <div>
                        <input type="password" name="password" placeholder="Password" value={formData.password} onChange={handleChange} required />
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                        <input type="date" name="dob" value={formData.dob} onChange={handleChange} style={{ color: formData.dob ? 'white' : 'var(--text-secondary)' }} />
                        <input type="text" name="mobile_number" placeholder="Mobile Number" value={formData.mobile_number} onChange={handleChange} />
                    </div>

                    <button type="submit" className="primary-btn" style={{ marginTop: '10px', width: '100%' }}>Sign Up</button>
                </form>

                <div style={{ marginTop: '25px', textAlign: 'center', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                    Already have an account? <Link to="/login" style={{ color: 'var(--primary)', fontWeight: '500', textDecoration: 'none' }}>Login</Link>
                </div>
            </div>
        </div>
    );
}

export default Register;
