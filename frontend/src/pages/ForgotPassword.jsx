import { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import api from '../api';

function ForgotPassword() {
    const navigate = useNavigate();
    const [email, setEmail] = useState('');
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            // Using API interceptor might assume auth? No, forgot password is public.
            // frontend/src/api.js likely attaches token if present.
            // But this route is unauthorized. Interceptor shouldn't block it.
            const res = await api.post('/auth/forgot-password', { email });
            setMessage(res.data.message);
            setError('');
        } catch (err) {
            setError(err.response?.data?.detail || "Failed to submit request");
        }
    };

    return (
        <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div className="card" style={{ width: '100%', maxWidth: '400px' }}>
                <h2 style={{ textAlign: 'center', marginBottom: '1.5rem', background: 'var(--gradient-primary)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>Forgot Password</h2>

                {message && <div style={{ padding: '10px', background: 'var(--success)', color: 'white', borderRadius: '4px', marginBottom: '20px' }}>{message}</div>}
                {error && <div style={{ padding: '10px', background: 'var(--danger)', color: 'white', borderRadius: '4px', marginBottom: '20px' }}>{error}</div>}

                <form onSubmit={handleSubmit}>
                    <div style={{ marginBottom: '20px' }}>
                        <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)' }}>Email</label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            style={{ width: '100%', padding: '12px', background: 'var(--bg-dark)', border: '1px solid var(--glass-border)', borderRadius: '8px', color: 'white' }}
                        />
                    </div>

                    <button type="submit" className="primary-btn" style={{ width: '100%', padding: '12px' }}>Submit Request</button>
                </form>

                <div style={{ marginTop: '20px', textAlign: 'center' }}>
                    <NavLink to="/login" style={{ color: 'var(--primary)', textDecoration: 'none', fontSize: '0.9rem' }}>Back to Login</NavLink>
                </div>
            </div>
        </div>
    );
}

export default ForgotPassword;
