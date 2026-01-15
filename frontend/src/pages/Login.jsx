import { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import AuthContext from '../context/AuthContext';

function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const { login } = useContext(AuthContext);
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        setError('');

        try {
            await login(email, password);
            navigate('/');
        } catch (err) {
            console.error(err);
            setError('Invalid email or password');
        }
    };

    return (
        <div style={{ padding: '50px', display: 'flex', justifyContent: 'center' }}>
            <div className="card" style={{ width: '400px', padding: '30px', borderRadius: '12px', background: '#1a1a1a' }}>
                <h2 style={{ textAlign: 'center', marginBottom: '20px' }}>Login</h2>
                {error && <p style={{ color: '#ff4d4f', textAlign: 'center' }}>{error}</p>}

                <form onSubmit={handleLogin}>
                    <div>
                        <label>Email:</label><br />
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>
                    <div style={{ marginTop: '10px' }}>
                        <label>Password:</label><br />
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>
                    <button type="submit" style={{ marginTop: '20px', width: '100%' }}>Login</button>
                </form>
            </div>
        </div>
    );
}

export default Login;