import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

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
            setTimeout(() => navigate('/login'), 3000);
        } catch (err) {
            setError(err.response?.data?.detail || 'Registration failed');
        }
    };

    return (
        <div style={{ padding: '50px', display: 'flex', justifyContent: 'center' }}>
            <div className="card" style={{ width: '500px', padding: '30px', borderRadius: '12px', background: '#1a1a1a' }}>
                <h2 style={{ textAlign: 'center', marginBottom: '20px' }}>Register</h2>
                {error && <p style={{ color: '#ff4d4f', textAlign: 'center' }}>{error}</p>}
                {success && <div style={{ color: '#52c41a', textAlign: 'center', marginBottom: '20px' }}>
                    Registration successful! <br /> Please wait for admin approval. Redirecting to login...
                </div>}

                <form onSubmit={handleRegister}>
                    <div>
                        <label>Username:</label><br />
                        <input type="text" name="username" value={formData.username} onChange={handleChange} required />
                    </div>
                    <div style={{ marginTop: '10px' }}>
                        <label>Email:</label><br />
                        <input type="email" name="email" value={formData.email} onChange={handleChange} required />
                    </div>
                    <div style={{ marginTop: '10px' }}>
                        <label>Password:</label><br />
                        <input type="password" name="password" value={formData.password} onChange={handleChange} required />
                    </div>
                    <div style={{ marginTop: '10px' }}>
                        <label>Date of Birth:</label><br />
                        <input type="date" name="dob" value={formData.dob} onChange={handleChange} />
                    </div>
                    <div style={{ marginTop: '10px' }}>
                        <label>Mobile Number:</label><br />
                        <input type="text" name="mobile_number" value={formData.mobile_number} onChange={handleChange} />
                    </div>


                    <button type="submit" style={{ marginTop: '20px', width: '100%' }}>Register</button>
                </form>
                <div style={{ marginTop: '15px', textAlign: 'center' }}>
                    <Link to="/login" style={{ color: '#1890ff' }}>Already have an account? Login</Link>
                </div>
            </div>
        </div>
    );
}

export default Register;
