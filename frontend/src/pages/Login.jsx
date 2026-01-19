import { useState, useContext, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import AuthContext from '../context/AuthContext';

function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [rememberMe, setRememberMe] = useState(false);
    const { login } = useContext(AuthContext);
    const navigate = useNavigate();

    // Check for saved email on mount
    useEffect(() => {
        const savedEmail = localStorage.getItem('rememberedEmail');
        if (savedEmail) {
            setEmail(savedEmail);
            setRememberMe(true);
        }
    }, []);

    const handleLogin = async (e) => {
        e.preventDefault();
        setError('');

        try {
            await login(email, password);

            if (rememberMe) {
                localStorage.setItem('rememberedEmail', email);
            } else {
                localStorage.removeItem('rememberedEmail');
            }

            navigate('/');
        } catch (err) {
            console.error(err);
            setError('Invalid email or password');
        }
    };

    return (
        <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1rem' }}>
            <div className="card" style={{ width: '100%', maxWidth: '400px', padding: '2.5rem', position: 'relative', overflow: 'hidden' }}>
                <div style={{ position: 'absolute', top: '-50%', right: '-50%', width: '200%', height: '200%', background: 'radial-gradient(circle, rgba(139,92,246,0.1) 0%, transparent 50%)', zIndex: -1 }}></div>

                <h2 style={{ textAlign: 'center', fontSize: '2rem', marginBottom: '0.5rem' }}>Welcome Back</h2>
                <p style={{ textAlign: 'center', color: 'var(--text-secondary)', marginBottom: '2rem' }}>Sign in to continue</p>

                {error && <div style={{ background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', padding: '12px', borderRadius: '8px', marginBottom: '20px', textAlign: 'center', fontSize: '0.9rem' }}>{error}</div>}

                <form onSubmit={handleLogin} style={{ display: 'grid', gap: '15px' }}>
                    <div>
                        <input
                            type="text"
                            placeholder="Username or Email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>
                    <div>
                        <input
                            type="password"
                            placeholder="Password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center' }}>
                        <input
                            type="checkbox"
                            checked={rememberMe}
                            onChange={(e) => setRememberMe(e.target.checked)}
                            id="rememberMe"
                            style={{ width: '18px', height: '18px', accentColor: 'var(--primary)', marginRight: '10px' }}
                        />
                        <label htmlFor="rememberMe" style={{ cursor: 'pointer', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Remember my ID</label>
                    </div>

                    <button type="submit" className="primary-btn" style={{ width: '100%' }}>Login</button>
                </form>

                <div style={{ marginTop: '25px', display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                    <Link to="/forgot-password" style={{ color: 'var(--primary)', textDecoration: 'none' }}>Forgot Password?</Link>
                    <span>New? <Link to="/register" style={{ color: 'var(--primary)', fontWeight: '500', textDecoration: 'none' }}>Register</Link></span>
                </div>
            </div>
        </div>
    );
}

export default Login;