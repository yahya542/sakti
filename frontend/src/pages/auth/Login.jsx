import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import { useTenantStore } from '../../store/tenantStore'
import Input from '../../components/ui/Input'
import Button from '../../components/ui/Button'
import LoadingSpinner from '../../components/ui/LoadingSpinner'

export default function Login() {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  })
  const [errors, setErrors] = useState({})
  
  const { login, isLoading, error } = useAuthStore()
  const { theme } = useTenantStore()
  const navigate = useNavigate()

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }))
    }
  }

  const validate = () => {
    const newErrors = {}
    if (!formData.username) newErrors.username = 'Username wajib diisi'
    if (!formData.password) newErrors.password = 'Password wajib diisi'
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!validate()) return

    const result = await login(formData)
    if (result.success) {
      navigate('/dashboard')
    }
  }

  return (
    <div>
      <div className="text-center mb-8">
        <div className="lg:hidden flex items-center justify-center gap-3 mb-4">
          <div 
            className="w-12 h-12 rounded-xl flex items-center justify-center text-white font-bold text-xl"
            style={{ backgroundColor: theme.primaryColor }}
          >
            S
          </div>
          <span className="text-2xl font-bold text-gray-900">{theme.appName}</span>
        </div>
        <h2 className="text-2xl font-bold text-gray-900">Masuk ke Akun</h2>
        <p className="text-gray-500 mt-2">Masukkan username dan password untuk melanjutkan</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        <Input
          label="Username"
          name="username"
          value={formData.username}
          onChange={handleChange}
          error={errors.username}
          placeholder="Masukkan username"
          autoComplete="username"
        />

        <Input
          label="Password"
          name="password"
          type="password"
          value={formData.password}
          onChange={handleChange}
          error={errors.password}
          placeholder="Masukkan password"
          autoComplete="current-password"
        />

        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
            {error}
          </div>
        )}

        <Button
          type="submit"
          className="w-full"
          isLoading={isLoading}
          size="lg"
        >
          Masuk
        </Button>
      </form>

      <div className="mt-6 text-center text-sm text-gray-500">
        <p>Demo Credentials:</p>
        <div className="mt-2 space-y-1">
          <p><span className="font-medium">Super Admin:</span> admin / admin123</p>
          <p><span className="font-medium">Admin Sekolah:</span> school_admin / school123</p>
          <p><span className="font-medium">Guru:</span> teacher / teacher123</p>
        </div>
      </div>
    </div>
  )
}