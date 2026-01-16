import { useContext } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import AuthContext from '../context/AuthContext';

function Navbar() {
    const { user, logout } = useContext(AuthContext);
    const navigate = useNavigate();
    const location = useLocation();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    if (!user) return null;

    const isActive = (path) => location.pathname === path ? 'active-link' : '';

    return (
        <nav className="navbar glass-panel">
            <div className="nav-container">
                <Link to="/" className="nav-brand">EMS <span style={{ color: 'var(--primary)', fontSize: '0.6em' }}>PRO</span></Link>

                <div className="nav-links">
                    <Link to="/" className={`nav-item ${isActive('/')}`}>Dashboard</Link>
                    {(user.role === 'admin' || user.role === 'manager') && (
                        <Link to="/admin/teams" className={`nav-item ${isActive('/admin/teams')}`}>Teams</Link>
                    )}
                    {user.role === 'admin' && (
                        <>
                            <Link to="/users" className={`nav-item ${isActive('/users')}`}>Users</Link>
                            <Link to="/admin/pending-users" className={`nav-item ${isActive('/admin/pending-users')}`}>Approvals</Link>
                        </>
                    )}
                </div>

                <div className="nav-user">
                    <div className="user-info">
                        <span className="user-email">{user.email}</span>
                        <span className="user-role">{user.role}</span>
                    </div>
                    <button onClick={handleLogout} className="logout-btn">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
                    </button>
                </div>
            </div>

            <style>{`
                .navbar {
                    background: rgba(18, 18, 18, 0.8);
                    backdrop-filter: blur(20px);
                    border-bottom: 1px solid var(--glass-border);
                    position: sticky;
                    top: 0;
                    z-index: 100;
                    width: 100%;
                    padding: 1.5rem;
                }
                .nav-container {
                    width: 100%;
                    margin: 0;
                    height: 70px;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                }
                .nav-brand {
                    font-size: 1.5rem;
                    font-weight: 800;
                    color: white;
                    text-decoration: none;
                    letter-spacing: -1px;
                }
                .nav-links {
                    display: flex;
                    gap: 1rem;
                }
                .nav-item {
                    color: var(--text-secondary);
                    text-decoration: none;
                    font-weight: 500;
                    padding: 0.5rem 1rem;
                    border-radius: 8px;
                    transition: all 0.2s;
                    font-size: 0.95rem;
                }
                .nav-item:hover, .nav-item.active-link {
                    color: white;
                    background: rgba(255,255,255,0.05);
                }
                .nav-item.active-link {
                    color: var(--primary);
                }
                .nav-user {
                    display: flex;
                    align-items: center;
                    gap: 1.5rem;
                }
                .user-info {
                    display: flex;
                    flex-direction: column;
                    align-items: flex-end;
                    line-height: 1.2;
                }
                .user-email {
                    font-size: 0.85rem;
                    font-weight: 500;
                }
                .user-role {
                    font-size: 0.7rem;
                    color: var(--text-secondary);
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }
                .logout-btn {
                    background: rgba(239, 68, 68, 0.1);
                    color: var(--danger);
                    padding: 8px;
                    border-radius: 8px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .logout-btn:hover {
                    background: rgba(239, 68, 68, 0.2);
                    transform: translateY(0);
                }
            `}</style>
        </nav>
    );
}

export default Navbar;
