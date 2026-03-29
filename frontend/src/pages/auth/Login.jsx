import { useState } from 'react'
import { useNavigate ,  Link} from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import { useTenantStore } from '../../store/tenantStore'
import Input from '../../components/ui/Input'
import Button from '../../components/ui/Button'
import LoadingSpinner from '../../components/ui/LoadingSpinner' 


export default function Login() {
  const [formData, setFormData] = useState({
    email: '',
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
    if (!formData.email) newErrors.email = 'email wajib diisi'
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
            
          </div>
          <span className="text-2xl font-bold text-gray-900">{theme.appName}</span>
        </div>
        <h2 className="text-2xl font-bold text-gray-900">Masuk ke Akun</h2>
        <p className="text-gray-500 mt-2">Masukkan email dan password untuk melanjutkan</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        <Input
          label="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          error={errors.email}
          placeholder="Masukkan email"
          autoComplete="email"
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

        <Button style={{ backgroundColor: theme.primaryColor }}
          type="submit"
          className="w-full"
          isLoading={false}
          size="lg"
        >
          Masuk
        </Button>
      </form>

      <div className="mt-6 text-center text-sm text-gray-500">
        <div className="mt-2 space-y-1">
           <p>Belum punya akun ? <Link to="/register" className="text-blue-500 hover:underline"> Daftarkan diri anda di sini</Link></p>
        </div>
      </div>
    </div>
  )
}

