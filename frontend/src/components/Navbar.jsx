import { useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import AuthContext from '../context/AuthContext';

function Navbar() {
    const { user, logout } = useContext(AuthContext);
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    if (!user) return null;

    return (
        <nav style={styles.nav}>
            <div style={styles.logo}>EMS</div>
            <div style={styles.links}>
                <Link to="/" style={styles.link}>Dashboard</Link>
                {user.role === 'admin' && <Link to="/users" style={styles.link}>Users</Link>}
                <div style={styles.user}>
                    <span style={{ marginRight: '10px' }}>{user.email} ({user.role})</span>
                    <button onClick={handleLogout} style={styles.logoutBtn}>Logout</button>
                </div>
            </div>
        </nav>
    );
}

const styles = {
    nav: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        background: '#1a1a1a',
        padding: '1rem 2rem',
        color: '#fff',
        marginBottom: '2rem',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
    },
    logo: {
        fontSize: '1.5rem',
        fontWeight: 'bold',
        color: '#646cff'
    },
    links: {
        display: 'flex',
        alignItems: 'center',
        gap: '20px'
    },
    link: {
        textDecoration: 'none',
        color: '#fff',
        fontWeight: '500'
    },
    logoutBtn: {
        background: '#ff4d4f',
        color: 'white',
        border: 'none',
        padding: '5px 15px',
        borderRadius: '4px',
        cursor: 'pointer'
    },
    user: {
        marginLeft: '20px',
        display: 'flex',
        alignItems: 'center'
    }
};

export default Navbar;
