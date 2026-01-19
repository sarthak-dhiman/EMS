import { useContext, useState, useEffect, useRef } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import AuthContext from '../context/AuthContext';
import api from '../api';
import { useToast } from '../context/ToastContext';

function Navbar() {
    const { user, logout } = useContext(AuthContext);
    const navigate = useNavigate();
    const location = useLocation();
    const [notifications, setNotifications] = useState([]);
    const [showNotifs, setShowNotifs] = useState(false);
    const notifRef = useRef(null);
    const { addToast } = useToast();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const fetchNotifications = async () => {
        if (!user) return;
        try {
            const res = await api.get('/notifications/');
            const newNotifsList = res.data;

            // Check for new notifications to show toast
            if (notifications.length > 0) {
                const existingIds = new Set(notifications.map(n => n.id));
                const newItems = newNotifsList.filter(n => !existingIds.has(n.id) && !n.is_read);

                newItems.forEach(item => {
                    addToast(item.title, item.message);
                });
            }

            setNotifications(newNotifsList);
        } catch (err) {
            console.error("Failed to fetch notifications", err);
        }
    };

    const markAsRead = async (id) => {
        try {
            await api.put(`/notifications/${id}/read`);
            setNotifications(notifications.map(n => n.id === id ? { ...n, is_read: true } : n));
        } catch (err) {
            console.error("Failed to mark as read", err);
        }
    };

    const markAllRead = async () => {
        try {
            await api.put(`/notifications/read-all`);
            setNotifications(notifications.map(n => ({ ...n, is_read: true })));
        } catch (err) {
            console.error("Failed to mark all read", err);
        }
    };

    useEffect(() => {
        if (user) {
            fetchNotifications();
            const interval = setInterval(fetchNotifications, 30000); // Poll every 30s
            return () => clearInterval(interval);
        }
    }, [user]);

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (notifRef.current && !notifRef.current.contains(event.target)) {
                setShowNotifs(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    if (!user) return null;

    const unreadCount = notifications.filter(n => !n.is_read).length;

    const isActive = (path) => location.pathname === path ? 'active-link' : '';

    return (
        <nav className="navbar glass-panel">
            <div className="nav-container">
                <Link to="/" className="nav-brand">EMS <span style={{ color: 'var(--primary)', fontSize: '0.6em' }}>PRO</span></Link>

                <div className="nav-links">
                    <Link to="/" className={`nav-item ${isActive('/')}`}>Dashboard</Link>
                    {user.role === 'admin' && (
                        <Link to="/admin/teams" className={`nav-item ${isActive('/admin/teams')}`}>Teams</Link>
                    )}
                    {user.role === 'manager' && (
                        <Link to="/team-dashboard" className={`nav-item ${isActive('/team-dashboard')}`}>My Team</Link>
                    )}
                    {user.role === 'admin' && (
                        <>
                            <Link to="/users" className={`nav-item ${isActive('/users')}`}>Users</Link>
                            <Link to="/admin/pending-users" className={`nav-item ${isActive('/admin/pending-users')}`}>Approvals</Link>
                        </>
                    )}
                </div>

                <div className="nav-user">
                    <div className="notification-wrapper" ref={notifRef}>
                        <button className="notif-bell" onClick={() => setShowNotifs(!showNotifs)}>
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>
                            {unreadCount > 0 && <span className="notif-badge">{unreadCount}</span>}
                        </button>

                        {showNotifs && (
                            <div className="notif-dropdown glass-panel">
                                <div className="notif-header">
                                    <span>Notifications</span>
                                    {unreadCount > 0 && <button onClick={markAllRead}>Mark all read</button>}
                                </div>
                                <div className="notif-list">
                                    {notifications.length === 0 ? (
                                        <div className="notif-empty">No notifications</div>
                                    ) : (
                                        notifications.map(n => (
                                            <div key={n.id} className={`notif-item ${n.is_read ? '' : 'unread'}`} onClick={() => markAsRead(n.id)}>
                                                <div className="notif-title">{n.title}</div>
                                                <div className="notif-msg">{n.message}</div>
                                                <div className="notif-time">{new Date(n.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
                                            </div>
                                        ))
                                    )}
                                </div>
                            </div>
                        )}
                    </div>

                    <Link to="/profile" className="user-info nav-item" style={{ textDecoration: 'none', color: 'inherit', display: 'flex', flexDirection: 'column', alignItems: 'flex-end', padding: '5px 10px' }}>
                        <span className="user-email">{user.email}</span>
                        <span className="user-role">{user.role}</span>
                    </Link>
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
                    padding: 0.8rem 1.5rem;
                }
                .nav-container {
                    width: 100%;
                    margin: 0;
                    height: 50px;
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
                .notification-wrapper {
                    position: relative;
                }
                .notif-bell {
                    background: none;
                    border: none;
                    color: var(--text-secondary);
                    padding: 8px;
                    border-radius: 8px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    position: relative;
                    transition: all 0.2s;
                }
                .notif-bell:hover {
                    color: white;
                    background: rgba(255,255,255,0.05);
                }
                .notif-badge {
                    position: absolute;
                    top: 2px;
                    right: 2px;
                    background: var(--primary);
                    color: black;
                    font-size: 0.65rem;
                    font-weight: 800;
                    min-width: 16px;
                    height: 16px;
                    border-radius: 10px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 0 4px;
                }
                .notif-dropdown {
                    position: absolute;
                    top: calc(100% + 15px);
                    right: 0;
                    width: 320px;
                    max-height: 480px;
                    background: rgba(20, 20, 20, 0.95);
                    border: 1px solid var(--glass-border);
                    border-radius: 12px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
                    display: flex;
                    flex-direction: column;
                    overflow: hidden;
                    animation: slideDown 0.2s ease-out;
                }
                @keyframes slideDown {
                    from { transform: translateY(-10px); opacity: 0; }
                    to { transform: translateY(0); opacity: 1; }
                }
                .notif-header {
                    padding: 1rem;
                    border-bottom: 1px solid var(--glass-border);
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    font-weight: 600;
                }
                .notif-header button {
                    background: none;
                    border: none;
                    color: var(--primary);
                    font-size: 0.8rem;
                    font-weight: 500;
                }
                .notif-list {
                    overflow-y: auto;
                }
                .notif-empty {
                    padding: 2rem;
                    text-align: center;
                    color: var(--text-secondary);
                    font-size: 0.9rem;
                }
                .notif-item {
                    padding: 1rem;
                    border-bottom: 1px solid rgba(255,255,255,0.05);
                    cursor: pointer;
                    transition: background 0.2s;
                }
                .notif-item:hover {
                    background: rgba(255,255,255,0.03);
                }
                .notif-item.unread {
                    background: rgba(110, 89, 255, 0.05);
                }
                .notif-title {
                    font-size: 0.9rem;
                    font-weight: 600;
                    margin-bottom: 0.2rem;
                }
                .notif-msg {
                    font-size: 0.8rem;
                    color: var(--text-secondary);
                    line-height: 1.4;
                }
                .notif-time {
                    font-size: 0.7rem;
                    color: var(--text-secondary);
                    margin-top: 0.5rem;
                    opacity: 0.6;
                }

            `}</style>
        </nav>
    );
}

export default Navbar;
