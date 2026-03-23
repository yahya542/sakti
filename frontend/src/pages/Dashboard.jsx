import { useQuery } from '@tanstack/react-query'
import { useAuthStore } from '../store/authStore'
import { useTenantStore } from '../store/tenantStore'
import api from '../lib/api'
import Card from '../components/ui/Card'

// Icons
const UsersIcon = () => (
  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
  </svg>
)

const BookIcon = () => (
  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
  </svg>
)

const CurrencyIcon = () => (
  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
)

const ActivityIcon = () => (
  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
  </svg>
)

export default function Dashboard() {
  const { user } = useAuthStore()
  const { theme, tenant } = useTenantStore()

  // Fetch dashboard stats
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => api.get('/api/dashboard/stats/'),
    enabled: !!user,
  })

  const getRoleLabel = (role) => {
    const labels = {
      super_admin: 'Super Admin',
      admin_school: 'Admin Sekolah',
      teacher: 'Guru/Ustadz',
      student: 'Siswa/Santri',
      parent: 'Wali Murid',
    }
    return labels[role] || role
  }

  const statCards = [
    {
      title: 'Total Siswa/Santri',
      value: stats?.students_count || 0,
      icon: <UsersIcon />,
      color: 'bg-blue-500',
    },
    {
      title: 'Total Guru/Ustadz',
      value: stats?.teachers_count || 0,
      icon: <BookIcon />,
      color: 'bg-green-500',
    },
    {
      title: 'Total Kelas/Madrasah',
      value: stats?.classes_count || 0,
      icon: <ActivityIcon />,
      color: 'bg-purple-500',
    },
    {
      title: 'Total Pembayaran',
      value: stats?.payments_count || 0,
      icon: <CurrencyIcon />,
      color: 'bg-yellow-500',
    },
  ]

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div 
        className="rounded-xl p-6 text-white"
        style={{ backgroundColor: theme.primaryColor }}
      >
        <h1 className="text-2xl font-bold mb-2">
          Selamat Datang, {user?.name || 'User'}!
        </h1>
        <p className="opacity-90">
          Anda login sebagai {getRoleLabel(user?.role)} di {theme.appName}
        </p>
        {tenant && (
          <p className="opacity-75 text-sm mt-2">
            {tenant.name}
          </p>
        )}
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => (
          <Card key={index} className="flex items-center gap-4">
            <div className={`p-3 rounded-lg ${stat.color} text-white`}>
              {stat.icon}
            </div>
            <div>
              <p className="text-sm text-gray-500">{stat.title}</p>
              <p className="text-2xl font-bold text-gray-900">
                {statsLoading ? '...' : stat.value}
              </p>
            </div>
          </Card>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Aksi Cepat">
          <div className="grid grid-cols-2 gap-4">
            <a 
              href="/academic/students"
              className="p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors text-center"
            >
              <UsersIcon />
              <span className="block mt-2 text-sm font-medium">Data Siswa</span>
            </a>
            <a 
              href="/activities/attendance"
              className="p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors text-center"
            >
              <ActivityIcon />
              <span className="block mt-2 text-sm font-medium">Presensi</span>
            </a>
            <a 
              href="/activities/scores"
              className="p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors text-center"
            >
              <BookIcon />
              <span className="block mt-2 text-sm font-medium">Input Nilai</span>
            </a>
            <a 
              href="/finance/invoices"
              className="p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors text-center"
            >
              <CurrencyIcon />
              <span className="block mt-2 text-sm font-medium">Tagihan SPP</span>
            </a>
          </div>
        </Card>

        {/* Recent Activity */}
        <Card title="Aktivitas Terbaru">
          <div className="space-y-4">
            <div className="flex items-start gap-3 pb-3 border-b border-gray-100">
              <div className="w-2 h-2 mt-2 rounded-full bg-green-500"></div>
              <div>
                <p className="text-sm text-gray-900">Presensi hari ini</p>
                <p className="text-xs text-gray-500">2 menit yang lalu</p>
              </div>
            </div>
            <div className="flex items-start gap-3 pb-3 border-b border-gray-100">
              <div className="w-2 h-2 mt-2 rounded-full bg-blue-500"></div>
              <div>
                <p className="text-sm text-gray-900">Nilai UTS ditambahkan</p>
                <p className="text-xs text-gray-500">1 jam yang lalu</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 mt-2 rounded-full bg-yellow-500"></div>
              <div>
                <p className="text-sm text-gray-900">Pembayaran SPP bulan Maret</p>
                <p className="text-xs text-gray-500">3 jam yang lalu</p>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}