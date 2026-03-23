import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, 
  MessageSquare, 
  Calendar, 
  ClipboardList, 
  Settings, 
  LogOut, 
  Bell,
  Search
} from 'lucide-react';
import Chatbot from '../components/Chatbot';

const API_BASE = 'http://127.0.0.1:8002';

const DashboardPage = () => {
  const [user, setUser] = useState<any>(null);
  const [activeTab, setActiveTab] = useState('overview');
  const navigate = useNavigate();
  const token = localStorage.getItem('token');

  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }
    fetchProfile();
  }, [token]);

  const fetchProfile = async () => {
    try {
      const res = await fetch(`${API_BASE}/profile`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setUser(data);
      } else {
        handleLogout();
      }
    } catch (e) {
      handleLogout();
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  if (!user) return null;

  return (
    <div className="dashboard-layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: '0.75rem', 
          marginBottom: '3rem',
          color: 'var(--primary)',
          fontSize: '1.5rem',
          fontWeight: 800
        }}>
          <div style={{ 
            background: 'var(--primary)', 
            color: 'white', 
            padding: '0.5rem', 
            borderRadius: '0.75rem' 
          }}>
            <MessageSquare size={24} />
          </div>
          <span>DentaFlow</span>
        </div>

        <nav style={{ flex: 1 }}>
          <NavItem 
            icon={<LayoutDashboard size={20} />} 
            label="Overview" 
            active={activeTab === 'overview'} 
            onClick={() => setActiveTab('overview')} 
          />
          <NavItem 
            icon={<MessageSquare size={20} />} 
            label="AI Assistant" 
            active={activeTab === 'chat'} 
            onClick={() => setActiveTab('chat')} 
          />
          <NavItem 
            icon={<Calendar size={20} />} 
            label="Appointments" 
            active={activeTab === 'appointments'} 
            onClick={() => setActiveTab('appointments')} 
          />
          <NavItem 
            icon={<ClipboardList size={20} />} 
            label="Records" 
            active={activeTab === 'records'} 
            onClick={() => setActiveTab('records')} 
          />
        </nav>

        <div style={{ marginTop: 'auto', borderTop: '1px solid var(--border-color)', paddingTop: '1.5rem' }}>
          <NavItem 
            icon={<Settings size={20} />} 
            label="Settings" 
            active={activeTab === 'settings'} 
            onClick={() => setActiveTab('settings')} 
          />
          <div className="nav-item" onClick={handleLogout} style={{ color: '#ef4444' }}>
            <LogOut size={20} />
            <span>Logout</span>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <header style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          marginBottom: '2rem'
        }}>
          <div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Hello, {user.full_name.split(' ')[0]}!</h2>
            <p style={{ color: 'var(--text-muted)' }}>Welcome to your DentaFlow Dashboard</p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
            <div style={{ 
              position: 'relative', 
              background: 'rgba(255,255,255,0.05)',
              borderRadius: '2rem',
              padding: '0.5rem 1rem',
              display: 'flex',
              alignItems: 'center',
              border: '1px solid var(--border-color)'
            }}>
              <Search size={18} style={{ color: 'var(--text-muted)', marginRight: '0.5rem' }} />
              <input 
                type="text" 
                placeholder="Search..." 
                style={{ background: 'none', border: 'none', color: 'white', outline: 'none', width: '150px' }}
              />
            </div>
            
            <button style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
              <Bell size={22} />
            </button>

            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '0.75rem',
              background: 'rgba(255,255,255,0.05)',
              padding: '0.4rem 0.8rem',
              borderRadius: '2rem',
              border: '1px solid var(--border-color)'
            }}>
              <div style={{ 
                width: '32px', 
                height: '32px', 
                borderRadius: '50%', 
                background: 'var(--primary)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: 700
              }}>
                {user.full_name[0]}
              </div>
              <span style={{ fontWeight: 600 }}>{user.full_name}</span>
            </div>
          </div>
        </header>

        <section style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {activeTab === 'chat' ? (
            <Chatbot />
          ) : activeTab === 'overview' ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
              {/* Quick Stats */}
              <div className="grid-cols-2" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.5rem' }}>
                <StatusCard 
                  title="Next Appointment" 
                  value="March 25, 10:00 AM" 
                  subtitle="Dr. Sarah Smith • Cleaning"
                  icon={<Calendar size={24} color="#60a5fa" />}
                />
                <StatusCard 
                  title="Medical Status" 
                  value="Healthy" 
                  subtitle="Last checkup: 2 months ago"
                  icon={<ClipboardList size={24} color="#34d399" />}
                />
                <StatusCard 
                  title="Notifications" 
                  value="2 New" 
                  subtitle="Checkup reminder & Prescription"
                  icon={<Bell size={24} color="#fbbf24" />}
                />
              </div>

              {/* Quick Actions */}
              <div style={{ 
                background: 'rgba(255,255,255,0.03)', 
                padding: '2rem', 
                borderRadius: '2rem', 
                border: '1px solid var(--border-color)' 
              }}>
                <h3 style={{ marginBottom: '1.5rem', fontSize: '1.25rem' }}>Quick Actions</h3>
                <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                  <ActionButton 
                    label="Book Appointment" 
                    icon={<Calendar size={20} />} 
                    onClick={() => setActiveTab('appointments')} 
                  />
                  <ActionButton 
                    label="Talk to AI" 
                    icon={<MessageSquare size={20} />} 
                    onClick={() => setActiveTab('chat')} 
                  />
                  <ActionButton 
                    label="View Records" 
                    icon={<ClipboardList size={20} />} 
                    onClick={() => setActiveTab('records')} 
                  />
                </div>
              </div>

              {/* Banner */}
              <div style={{ 
                background: 'linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)', 
                padding: '2.5rem', 
                borderRadius: '2rem',
                color: 'white',
                position: 'relative',
                overflow: 'hidden'
              }}>
                <div style={{ position: 'relative', zIndex: 1, maxWidth: '60%' }}>
                  <h3 style={{ fontSize: '1.75rem', fontWeight: 800, marginBottom: '0.5rem' }}>Your Smile Matters!</h3>
                  <p style={{ opacity: 0.9 }}>Ask our AI assistant any questions about your dental health or book your next checkup today.</p>
                  <button 
                    onClick={() => setActiveTab('chat')}
                    className="btn-primary" 
                    style={{ background: 'white', color: '#1e40af', width: 'auto', marginTop: '1.5rem', padding: '0.75rem 1.5rem' }}
                  >
                    Start Chatting
                  </button>
                </div>
                <div style={{ 
                  position: 'absolute', right: '-20px', bottom: '-20px', opacity: 0.2, transform: 'rotate(-15deg)' 
                }}>
                  <MessageSquare size={200} />
                </div>
              </div>
            </div>
          ) : (
            <div style={{ 
              flex: 1, 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              flexDirection: 'column',
              background: 'rgba(15, 23, 42, 0.4)',
              borderRadius: '2rem',
              border: '1px solid var(--border-color)'
            }}>
              <div style={{ color: 'var(--primary)', marginBottom: '1rem' }}>
                <LayoutDashboard size={48} />
              </div>
              <h3 style={{ fontSize: '1.25rem', color: 'white' }}>{activeTab.charAt(0).toUpperCase() + activeTab.slice(1)} Module</h3>
              <p style={{ color: 'var(--text-muted)' }}>This section is currently under development.</p>
            </div>
          )}
        </section>
      </main>
    </div>
  );
};

const NavItem = ({ icon, label, active, onClick }: any) => (
  <div className={`nav-item ${active ? 'active' : ''}`} onClick={onClick}>
    {icon}
    <span>{label}</span>
  </div>
);

const StatusCard = ({ title, value, subtitle, icon }: any) => (
  <div style={{ 
    background: 'rgba(255,255,255,0.03)', 
    padding: '1.5rem', 
    borderRadius: '1.5rem', 
    border: '1px solid var(--border-color)',
    display: 'flex',
    gap: '1rem'
  }}>
    <div style={{ 
      background: 'rgba(255,255,255,0.05)', 
      padding: '0.75rem', 
      borderRadius: '1rem',
      height: 'fit-content'
    }}>
      {icon}
    </div>
    <div>
      <h4 style={{ color: 'var(--text-muted)', fontSize: '0.875rem', fontWeight: 500, marginBottom: '0.25rem' }}>{title}</h4>
      <div style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.25rem' }}>{value}</div>
      <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>{subtitle}</div>
    </div>
  </div>
);

const ActionButton = ({ label, icon, onClick }: any) => (
  <button 
    onClick={onClick}
    className="btn-primary" 
    style={{ 
      background: 'rgba(255,255,255,0.05)', 
      border: '1px solid var(--border-color)',
      color: 'white',
      width: 'auto',
      padding: '0.75rem 1.25rem'
    }}
  >
    {icon}
    {label}
  </button>
);

export default DashboardPage;
