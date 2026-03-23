import { useState } from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import { useTenantStore } from '../../store/tenantStore'

// Icons
const MenuIcon = () => (
  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
  </svg>
)

const LogoutIcon = () => (
  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
  </svg>
)

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
  { 
    label: 'Akademik', 
    icon: 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253',
    children: [
      { path: '/academic/students', label: 'Siswa/Santri' },
      { path: '/academic/teachers', label: 'Guru/Ustadz' },
      { path: '/academic/classes', label: 'Kelas/Madrasah' },
      { path: '/academic/subjects', label: 'Mapel/Kitab' },
    ]
  },
  { 
    label: 'Activities', 
    icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01',
    children: [
      { path: '/activities/attendance', label: 'Presensi' },
      { path: '/activities/scores', label: 'Nilai' },
      { path: '/activities/timeline', label: 'Timeline' },
    ]
  },
  { 
    label: 'Keuangan', 
    icon: 'M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z',
    children: [
      { path: '/finance/invoices', label: 'Tagihan SPP' },
      { path: '/finance/payments', label: 'Pembayaran' },
    ]
  },
  { path: '/smart-linking', label: 'Smart Linking', icon: 'M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1' },
  { path: '/settings', label: 'Pengaturan', icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z' },
]

export default function MainLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [expandedMenus, setExpandedMenus] = useState({})
  const { user, logout } = useAuthStore()
  const { theme } = useTenantStore()
  const navigate = useNavigate()
  const location = useLocation()

  const toggleMenu = (label) => {
    setExpandedMenus(prev => ({
      ...prev,
      [label]: !prev[label]
    }))
  }

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const getRoleBadge = (role) => {
    const badges = {
      super_admin: { bg: 'bg-purple-100', text: 'text-purple-800', label: 'Super Admin' },
      admin_school: { bg: 'bg-blue-100', text: 'text-blue-800', label: 'Admin Sekolah' },
      teacher: { bg: 'bg-green-100', text: 'text-green-800', label: 'Guru/Ustadz' },
      student: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Siswa/Santri' },
      parent: { bg: 'bg-pink-100', text: 'text-pink-800', label: 'Wali Murid' },
    }
    return badges[role] || badges.student
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside 
        className={`
          fixed inset-y-0 left-0 z-40 bg-white border-r border-gray-200 
          transition-all duration-300 flex flex-col
          ${sidebarOpen ? 'w-64' : 'w-20'}
        `}
      >
        {/* Logo */}
        <div className="h-16 flex items-center px-4 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div 
              className="w-10 h-10 rounded-lg flex items-center justify-center text-white font-bold text-lg"
              style={{ backgroundColor: theme.primaryColor }}
            >
              S
            </div>
            {sidebarOpen && (
              <span className="font-bold text-gray-900">{theme.appName}</span>
            )}
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-4 px-3 scrollbar-thin">
          {navItems.map((item, index) => (
            <div key={index} className="mb-1">
              {item.children ? (
                <>
                  <button
                    onClick={() => toggleMenu(item.label)}
                    className={`
                      w-full flex items-center gap-3 px-3 py-2.5 rounded-lg 
                      text-gray-700 hover:bg-gray-100 transition-colors
                      ${expandedMenus[item.label] ? 'bg-gray-100' : ''}
                    `}
                  >
                    <svg className="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={item.icon} />
                    </svg>
                    {sidebarOpen && (
                      <>
                        <span className="flex-1 text-left text-sm font-medium">{item.label}</span>
                        <svg 
                          className={`w-4 h-4 transition-transform ${expandedMenus[item.label] ? 'rotate-180' : ''}`} 
                          fill="none" viewBox="0 0 24 24" stroke="currentColor"
                        >
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </>
                    )}
                  </button>
                  {expandedMenus[item.label] && sidebarOpen && (
                    <div className="ml-8 mt-1 space-y-1">
                      {item.children.map((child, childIndex) => (
                        <a
                          key={childIndex}
                          href={child.path}
                          className={`
                            block px-3 py-2 rounded-lg text-sm
                            ${location.pathname === child.path 
                              ? 'bg-primary-50 text-primary-700 font-medium' 
                              : 'text-gray-600 hover:bg-gray-50'
                            }
                          `}
                        >
                          {child.label}
                        </a>
                      ))}
                    </div>
                  )}
                </>
              ) : (
                <a
                  href={item.path}
                  className={`
                    flex items-center gap-3 px-3 py-2.5 rounded-lg 
                    ${location.pathname === item.path
                      ? 'bg-primary-50 text-primary-700 font-medium'
                      : 'text-gray-700 hover:bg-gray-100'
                    }
                  `}
                >
                  <svg className="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={item.icon} />
                  </svg>
                  {sidebarOpen && <span className="text-sm font-medium">{item.label}</span>}
                </a>
              )}
            </div>
          ))}
        </nav>

        {/* User Info & Logout */}
        <div className="border-t border-gray-200 p-4">
          {sidebarOpen ? (
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center">
                  <span className="text-sm font-medium text-gray-600">
                    {user?.name?.charAt(0) || 'U'}
                  </span>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">{user?.name || 'User'}</p>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${getRoleBadge(user?.role).bg} ${getRoleBadge(user?.role).text}`}>
                    {getRoleBadge(user?.role).label}
                  </span>
                </div>
              </div>
              <button
                onClick={handleLogout}
                className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                title="Logout"
              >
                <LogoutIcon />
              </button>
            </div>
          ) : (
            <button
              onClick={handleLogout}
              className="w-full p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
              title="Logout"
            >
              <LogoutIcon />
            </button>
          )}
        </div>
      </aside>

      {/* Main Content */}
      <main className={`flex-1 transition-all duration-300 ${sidebarOpen ? 'ml-64' : 'ml-20'}`}>
        {/* Header */}
        <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6 sticky top-0 z-30">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg"
          >
            <MenuIcon />
          </button>

          <div className="flex items-center gap-4">
            <div className="text-sm text-gray-600">
              <span className="font-medium">{new Date().toLocaleDateString('id-ID', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}</span>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <div className="p-6">
          <Outlet />
        </div>
      </main>
    </div>
  )
}