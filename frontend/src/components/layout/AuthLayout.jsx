import { Outlet } from 'react-router-dom'
import { useTenantStore } from '../../store/tenantStore'

export default function AuthLayout() {
  const { theme } = useTenantStore()

  return (
    <div className="min-h-screen flex">
      {/* Left Side - Branding */}
      <div 
        className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-primary-600 to-primary-800 flex-col justify-between p-12"
        style={{ backgroundColor: theme.primaryColor }}
      >
        <div>
          <div className="flex items-center gap-3 mb-8">
            <div className="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center text-white font-bold text-xl">
              S
            </div>
            <span className="text-2xl font-bold text-white">{theme.appName}</span>
          </div>
          <h1 className="text-4xl font-bold text-white mb-4">
            Sistem Akademik Terpadu Indonesia
          </h1>
          <p className="text-primary-100 text-lg">
            Kelola administrasi, akademik, keuangan, dan komunikasi dalam satu platform digital untuk sekolah dan pesantren di Indonesia.
          </p>
        </div>

        <div className="space-y-4">
          <div className="flex items-center gap-3 text-primary-100">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            <span>Multi-Tenancy untuk banyak sekolah</span>
          </div>
          <div className="flex items-center gap-3 text-primary-100">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            <span>Smart Linking otomatis No KK</span>
          </div>
          <div className="flex items-center gap-3 text-primary-100">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            <span>Real-time Timeline untuk wali murid</span>
          </div>
          <div className="flex items-center gap-3 text-primary-100">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            <span>Integrasi Payment Gateway (Midtrans/Xendit)</span>
          </div>
        </div>

        <div className="text-primary-200 text-sm">
          © 2026 Sajakcodingan. Sinergi Pendidikan dalam Satu Genggaman.
        </div>
      </div>

      {/* Right Side - Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-gray-50">
        <div className="w-full max-w-md">
          <Outlet />
        </div>
      </div>
    </div>
  )
}