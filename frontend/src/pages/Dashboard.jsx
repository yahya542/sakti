import { useQuery } from '@tanstack/react-query'
import { useAuthStore } from '../store/authStore'
import { useTenantStore } from '../store/tenantStore'
import api from '../lib/api'
import Card from '../components/ui/Card'
import LoadingSpinner from '../components/ui/LoadingSpinner'

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

const CheckCircleIcon = () => (
  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
)

const CalendarIcon = () => (
  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
  </svg>
)

const ChartIcon = () => (
  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
  </svg>
)

const BellIcon = () => (
  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.658 6 8.618 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
  </svg>
)

const SchoolIcon = () => (
  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m0 0h-5m-2 0H9m-2 0H7a2 2 0 01-2-2v-4a2 2 0 012-2h2m4 0h6" />
  </svg>
)

const FlagIcon = () => (
  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9 13.5v9" />
  </svg>
)

// Quick action button component
function QuickAction({ href, icon, label, description, color }) {
  return (
    <a 
      href={href}
      className="p-4 border border-gray-200 rounded-lg hover:border-gray-300 hover:bg-gray-50 transition-all group"
    >
      <div className={`w-10 h-10 rounded-lg ${color} text-white flex items-center justify-center mb-3 group-hover:scale-110 transition-transform`}>
        {icon}
      </div>
      <span className="block text-sm font-semibold text-gray-900">{label}</span>
      {description && (
        <span className="block text-xs text-gray-500 mt-1">{description}</span>
      )}
    </a>
  )
}

// Dashboard for SUPER ADMIN - Full system overview
function SuperAdminDashboard({ stats, isLoading }) {
  const statCards = [
    { title: 'Total Tenant/Sekolah', value: stats?.tenants_count || 0, icon: <SchoolIcon />, color: 'bg-purple-600' },
    { title: 'Total Siswa/Santri', value: stats?.students_count || 0, icon: <UsersIcon />, color: 'bg-blue-500' },
    { title: 'Total Guru/Ustadz', value: stats?.teachers_count || 0, icon: <BookIcon />, color: 'bg-green-500' },
    { title: 'Total Kelas/Madrasah', value: stats?.classes_count || 0, icon: <ActivityIcon />, color: 'bg-orange-500' },
  ]

  return (
    <div className="space-y-6">
      {/* Stats - Full Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => (
          <Card key={index} className="flex items-center gap-4">
            <div className={`p-3 rounded-lg ${stat.color} text-white`}>
              {stat.icon}
            </div>
            <div>
              <p className="text-sm text-gray-500">{stat.title}</p>
              <p className="text-2xl font-bold text-gray-900">
                {isLoading ? '...' : stat.value}
              </p>
            </div>
          </Card>
        ))}
      </div>

      {/* Quick Actions - Super Admin */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <QuickAction href="/tenants" icon={<FlagIcon />} label="Kelola Tenant" description="Kelola sekolah/pesantren" color="bg-purple-600" />
        <QuickAction href="/academic/students" icon={<UsersIcon />} label="Data Siswa" description="Kelola siswa/santri" color="bg-blue-500" />
        <QuickAction href="/academic/teachers" icon={<BookIcon />} label="Data Guru" description="Kelola guru/ustadz" color="bg-green-500" />
        <QuickAction href="/settings/rbac" icon={<ActivityIcon />} label="Pengaturan RBAC" description="Kelola peran & izin" color="bg-orange-500" />
      </div>
    </div>
  )
}

// Dashboard for ADMIN SCHOOL - School management
function AdminSchoolDashboard({ stats, isLoading }) {
  const statCards = [
    { title: 'Total Siswa/Santri', value: stats?.students_count || 0, icon: <UsersIcon />, color: 'bg-blue-500' },
    { title: 'Total Guru/Ustadz', value: stats?.teachers_count || 0, icon: <BookIcon />, color: 'bg-green-500' },
    { title: 'Total Kelas/Madrasah', value: stats?.classes_count || 0, icon: <ActivityIcon />, color: 'bg-purple-500' },
    { title: 'Pembayaran Tertunda', value: stats?.pending_payments || 0, icon: <CurrencyIcon />, color: 'bg-yellow-500' },
  ]

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => (
          <Card key={index} className="flex items-center gap-4">
            <div className={`p-3 rounded-lg ${stat.color} text-white`}>
              {stat.icon}
            </div>
            <div>
              <p className="text-sm text-gray-500">{stat.title}</p>
              <p className="text-2xl font-bold text-gray-900">
                {isLoading ? '...' : stat.value}
              </p>
            </div>
          </Card>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <QuickAction href="/academic/students" icon={<UsersIcon />} label="Data Siswa" color="bg-blue-500" />
        <QuickAction href="/academic/teachers" icon={<BookIcon />} label="Data Guru" color="bg-green-500" />
        <QuickAction href="/academic/classes" icon={<ActivityIcon />} label="Kelas" color="bg-purple-500" />
        <QuickAction href="/finance/invoices" icon={<CurrencyIcon />} label="Tagihan SPP" color="bg-yellow-500" />
        <QuickAction href="/activities/attendance" icon={<CalendarIcon />} label="Absensi" color="bg-indigo-500" />
        <QuickAction href="/activities/scores" icon={<ChartIcon />} label="Input Nilai" color="bg-pink-500" />
        <QuickAction href="/smart-linking" icon={<UsersIcon />} label="Smart Linking" color="bg-cyan-500" />
        <QuickAction href="/settings" icon={<ActivityIcon />} label="Pengaturan" color="bg-gray-500" />
      </div>
    </div>
  )
}

// Dashboard for TEACHER - Class management
function TeacherDashboard({ stats, isLoading, myStudents }) {
  const statCards = [
    { title: 'Siswa Kelas Saya', value: myStudents?.count || 0, icon: <UsersIcon />, color: 'bg-blue-500' },
    { title: 'Mata Pelajaran', value: stats?.subjects_count || 0, icon: <BookIcon />, color: 'bg-green-500' },
    { title: 'Absensi Hari Ini', value: stats?.today_attendance || 0, icon: <CheckCircleIcon />, color: 'bg-purple-500' },
    { title: 'Nilai Belum Input', value: stats?.pending_scores || 0, icon: <ActivityIcon />, color: 'bg-orange-500' },
  ]

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => (
          <Card key={index} className="flex items-center gap-4">
            <div className={`p-3 rounded-lg ${stat.color} text-white`}>
              {stat.icon}
            </div>
            <div>
              <p className="text-sm text-gray-500">{stat.title}</p>
              <p className="text-2xl font-bold text-gray-900">
                {isLoading ? '...' : stat.value}
              </p>
            </div>
          </Card>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <QuickAction href="/academic/students" icon={<UsersIcon />} label="Daftar Siswa" color="bg-blue-500" />
        <QuickAction href="/activities/attendance" icon={<CalendarIcon />} label="Input Absensi" color="bg-purple-500" />
        <QuickAction href="/activities/scores" icon={<ChartIcon />} label="Input Nilai" color="bg-green-500" />
        <QuickAction href="/activities/timeline" icon={<BellIcon />} label="Timeline" color="bg-orange-500" />
      </div>

      {/* My Students List */}
      <Card title="Siswa Kelas Saya">
        {isLoading ? (
          <LoadingSpinner />
        ) : myStudents?.results?.length > 0 ? (
          <div className="divide-y divide-gray-100">
            {myStudents.results.slice(0, 5).map((student) => (
              <div key={student.id} className="py-3 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-medium">
                    {student.first_name?.[0] || 'S'}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{student.full_name || `${student.first_name} ${student.last_name}`}</p>
                    <p className="text-xs text-gray-500">{student.email}</p>
                  </div>
                </div>
                <span className={`px-2 py-1 text-xs rounded-full ${student.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'}`}>
                  {student.is_active ? 'Aktif' : 'Nonaktif'}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-gray-500">Belum ada siswa di kelas Anda.</p>
        )}
      </Card>
    </div>
  )
}

// Dashboard for STUDENT - Personal info
function StudentDashboard({ stats, isLoading, myGrades, myAttendance }) {
  const statCards = [
    { title: 'Rata-rata Nilai', value: stats?.average_score || '-', icon: <ChartIcon />, color: 'bg-blue-500' },
    { title: 'Kehadiran', value: `${stats?.attendance_rate || 0}%`, icon: <CheckCircleIcon />, color: 'bg-green-500' },
    { title: 'Kehadiran Today', value: myAttendance?.today || '-', icon: <CalendarIcon />, color: 'bg-purple-500' },
    { title: 'Status Pembayaran', value: stats?.payment_status || 'Lunas', icon: <CurrencyIcon />, color: 'bg-yellow-500' },
  ]

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {statCards.map((stat, index) => (
          <Card key={index} className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${stat.color} text-white`}>
              {stat.icon}
            </div>
            <div>
              <p className="text-xs text-gray-500">{stat.title}</p>
              <p className="text-lg font-bold text-gray-900">
                {isLoading ? '...' : stat.value}
              </p>
            </div>
          </Card>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <QuickAction href="/activities/scores" icon={<ChartIcon />} label="Nilai Saya" color="bg-blue-500" />
        <QuickAction href="/activities/attendance" icon={<CalendarIcon />} label="Kehadiran" color="bg-green-500" />
        <QuickAction href="/finance/payments" icon={<CurrencyIcon />} label="Pembayaran" color="bg-yellow-500" />
      </div>

      {/* Recent Grades */}
      <Card title="Nilai Terbaru">
        {isLoading ? (
          <LoadingSpinner />
        ) : myGrades?.results?.length > 0 ? (
          <div className="space-y-3">
            {myGrades.results.slice(0, 5).map((grade) => (
              <div key={grade.id} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                <div>
                  <p className="text-sm font-medium text-gray-900">{grade.title}</p>
                  <p className="text-xs text-gray-500">{grade.subject_name}</p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold text-gray-900">{grade.score}</p>
                  <p className="text-xs text-gray-500">{grade.score_type}</p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-gray-500">Belum ada nilai.</p>
        )}
      </Card>
    </div>
  )
}

// Dashboard for PARENT - Children info
function ParentDashboard({ stats, isLoading, children }) {
  const statCards = [
    { title: 'Anak Terhubung', value: children?.count || 0, icon: <UsersIcon />, color: 'bg-blue-500' },
    { title: 'Notifikasi Baru', value: stats?.new_notifications || 0, icon: <BellIcon />, color: 'bg-red-500' },
    { title: 'Tagihan Tertunda', value: stats?.pending_invoices || 0, icon: <CurrencyIcon />, color: 'bg-yellow-500' },
    { title: 'Pembayaran Lunas', value: stats?.paid_invoices || 0, icon: <CheckCircleIcon />, color: 'bg-green-500' },
  ]

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {statCards.map((stat, index) => (
          <Card key={index} className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${stat.color} text-white`}>
              {stat.icon}
            </div>
            <div>
              <p className="text-xs text-gray-500">{stat.title}</p>
              <p className="text-lg font-bold text-gray-900">
                {isLoading ? '...' : stat.value}
              </p>
            </div>
          </Card>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <QuickAction href="/activities/timeline" icon={<BellIcon />} label="Aktivitas" color="bg-purple-500" />
        <QuickAction href="/activities/scores" icon={<ChartIcon />} label="Nilai Anak" color="bg-blue-500" />
        <QuickAction href="/activities/attendance" icon={<CalendarIcon />} label="Kehadiran" color="bg-green-500" />
        <QuickAction href="/finance/invoices" icon={<CurrencyIcon />} label="Pembayaran" color="bg-yellow-500" />
      </div>

      {/* Children List */}
      <Card title="Anak Saya">
        {isLoading ? (
          <LoadingSpinner />
        ) : children?.results?.length > 0 ? (
          <div className="space-y-3">
            {children.results.map((child) => (
              <div key={child.id} className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-medium">
                    {child.first_name?.[0] || 'A'}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{child.full_name || `${child.first_name} ${child.last_name}`}</p>
                    <p className="text-xs text-gray-500">{child.class_name || 'Kelas belum ditentukan'}</p>
                  </div>
                </div>
                <a href={`/activities/scores?student=${child.id}`} className="text-sm text-blue-600 hover:underline">
                  Lihat Nilai
                </a>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-gray-500">Belum ada anak terhubung. Gunakan menu Smart Linking untuk menghubungkan akun anak.</p>
        )}
      </Card>
    </div>
  )
}

export default function Dashboard() {
  const { user } = useAuthStore()
  const { theme, tenant } = useTenantStore()
  const role = user?.role

  // Fetch dashboard stats based on role
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard-stats', role],
    queryFn: () => api.get('/dashboard/stats/'),
    enabled: !!user,
  })

  // Fetch role-specific data
  const { data: myStudents } = useQuery({
    queryKey: ['my-students'],
    queryFn: () => api.get('/academic/students/'),
    enabled: role === 'teacher' && !!user,
  })

  const { data: myGrades } = useQuery({
    queryKey: ['my-grades'],
    queryFn: () => api.get('/activities/scores/'),
    enabled: role === 'student' && !!user,
  })

  const { data: myAttendance } = useQuery({
    queryKey: ['my-attendance'],
    queryFn: () => api.get('/activities/attendances/'),
    enabled: role === 'student' && !!user,
  })

  const { data: children } = useQuery({
    queryKey: ['children'],
    queryFn: () => api.get('/smart-linking/links/'),
    enabled: role === 'parent' && !!user,
  })

  const getRoleLabel = (r) => {
    const labels = {
      super_admin: 'Super Admin',
      admin_school: 'Admin Sekolah',
      teacher: 'Guru/Ustadz',
      student: 'Siswa/Santri',
      parent: 'Wali Murid',
    }
    return labels[r] || r
  }

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div 
        className="rounded-xl p-6 text-white"
        style={{ backgroundColor: theme.primaryColor }}
      >
        <h1 className="text-2xl font-bold mb-2">
          Selamat Datang, {user?.first_name || user?.name || 'User'}!
        </h1>
        <p className="opacity-90">
          Anda login sebagai {getRoleLabel(role)} di {theme.appName}
        </p>
        {tenant && (
          <p className="opacity-75 text-sm mt-2">
            {tenant.name}
          </p>
        )}
      </div>

      {/* Role-specific Dashboard Content */}
      {role === 'super_admin' && <SuperAdminDashboard stats={stats} isLoading={statsLoading} />}
      {role === 'admin_school' && <AdminSchoolDashboard stats={stats} isLoading={statsLoading} />}
      {role === 'teacher' && <TeacherDashboard stats={stats} isLoading={statsLoading} myStudents={myStudents} />}
      {role === 'student' && <StudentDashboard stats={stats} isLoading={statsLoading} myGrades={myGrades} myAttendance={myAttendance} />}
      {role === 'parent' && <ParentDashboard stats={stats} isLoading={statsLoading} children={children} />}
      
      {/* Default fallback for unknown roles */}
      {!['super_admin', 'admin_school', 'teacher', 'student', 'parent'].includes(role) && (
        <Card>
          <p className="text-gray-500">Dashboard tidak tersedia untuk peran ini.</p>
        </Card>
      )}
    </div>
  )
}