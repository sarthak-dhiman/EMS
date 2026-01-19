import { useContext } from 'react';
import Navbar from '../components/Navbar';
import AuthContext from '../context/AuthContext';

function Profile() {
    const { user } = useContext(AuthContext);

    if (!user) return <div style={{ color: 'white', textAlign: 'center', marginTop: '50px' }}>Loading...</div>;

    // Helper to format checks
    const InfoRow = ({ label, value }) => (
        <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
            <span style={{ color: 'var(--text-secondary)' }}>{label}</span>
            <span style={{ color: 'white', fontWeight: '500' }}>{value || 'N/A'}</span>
        </div>
    );

    return (
        <div className="dashboard-container">
            <Navbar />
            <div className="content" style={{ display: 'flex', justifyContent: 'center', marginTop: '40px' }}>
                <div className="card" style={{ maxWidth: '600px', width: '100%', padding: '0', overflow: 'hidden' }}>
                    <div style={{
                        background: 'linear-gradient(to right, #4f46e5, #8b5cf6)',
                        padding: '40px 20px',
                        textAlign: 'center'
                    }}>
                        <div style={{
                            width: '80px', height: '80px', background: 'white', borderRadius: '50%',
                            margin: '0 auto 15px', display: 'flex', alignItems: 'center', justifyContent: 'center',
                            fontSize: '2rem', color: '#4f46e5', fontWeight: 'bold'
                        }}>
                            {user.username.charAt(0).toUpperCase()}
                        </div>
                        <h2 style={{ margin: 0, color: 'white' }}>{user.username}</h2>
                        <p style={{ margin: '5px 0 0', color: 'rgba(255,255,255,0.8)', fontSize: '0.9rem' }}>{user.email}</p>
                    </div>

                    <div style={{ padding: '30px' }}>
                        <h3 style={{ marginBottom: '20px', fontSize: '1.2rem' }}>Personal Information</h3>
                        <InfoRow label="User ID" value={user.id} />
                        <InfoRow label="Role" value={user.role ? user.role.toUpperCase() : 'N/A'} />
                        <InfoRow label="Team" value={user.team_name} />
                        <InfoRow label="Joined" value={new Date(user.created_at || Date.now()).toLocaleDateString()} />
                        <InfoRow label="Date of Birth" value={user.dob} />
                        <InfoRow label="Mobile" value={user.mobile_number} />

                        <div style={{ marginTop: '30px', textAlign: 'center' }}>
                            <button onClick={() => alert("Edit Profile Feature Coming Soon (Backend Ready, UI Pending)")} style={{
                                background: 'transparent',
                                border: '1px solid var(--primary)',
                                color: 'var(--primary)',
                                padding: '10px 20px',
                                borderRadius: '8px',
                                cursor: 'pointer',
                                transition: 'all 0.2s'
                            }}>
                                Edit Profile
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Profile;
