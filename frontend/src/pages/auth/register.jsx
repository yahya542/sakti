import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import { useTenantStore } from '../../store/tenantStore'
import Input from '../../components/ui/Input'
import Button from '../../components/ui/Button'
import LoadingSpinner from '../../components/ui/LoadingSpinner'

export default function Register() {
  const navigate = useNavigate()
  const { theme } = useTenantStore()
  const { register, isLoading, error: authError } = useAuthStore()

  const [formData, setFormData] = useState({
    email: '',
    password: '',
    password_confirm: '',
    first_name: '',
    last_name: '',
    role: 'student',
    phone: '',
    no_kk: '',
    profile: {
      employee_id: '',
      student_id: '',
      address: '',
      place_of_birth: '',
      date_of_birth: '',
      gender: 'male'
    }
  })

  const handleChange = (e) => {
    const { name, value } = e.target

    if (name.includes('.')) {
      // Pecah 'profile.address' menjadi ['profile', 'address']
      const [parent, child] = name.split('.')

      setFormData(prev => ({
        ...prev,
        [parent]: {
          ...prev[parent],
          [child]: value // Ini akan mengisi 'address' di dalam 'profile'
        }
      }))
    } else {
      setFormData(prev => ({ ...prev, [name]: value }))
    }
  }


  const handleSubmit = async (e) => {
    e.preventDefault()

    if (formData.password !== formData.password_confirm) {
      // Anda bisa set error manual di sini
      alert("Password dan Konfirmasi Password tidak cocok!")
      return
    }

    const result = await register(formData)
    if (result.success) {
      navigate('/login')
    }
  }


  return (
    <div className="max-w-md mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900">Daftar Akun Baru</h2>
        <p className="text-gray-500 mt-2">Lengkapi data di bawah untuk mendaftar</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Pilihan Role */}
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">Daftar Sebagai</label>
          <select
            name="role"
            value={formData.role}
            onChange={handleChange}
            className="w-full px-3 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          >
            <option value="teacher">Guru / Ustadz</option>
            <option value="student">Siswa / Santri</option>
            <option value="parent">Wali Murid / Orang Tua</option>
          </select>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <Input label="Nama Depan" name="first_name" value={formData.first_name} onChange={handleChange} required />
          <Input label="Nama Belakang" name="last_name" value={formData.last_name} onChange={handleChange} required />
        </div>

        <Input label="Email" name="email" type="email" value={formData.email} onChange={handleChange} required />
        <Input label="No. Telepon" name="phone" value={formData.phone} onChange={handleChange} />

        {/* No KK - wajib untuk student dan parent */}
        <Input 
          label="No. KK" 
          name="no_kk" 
          value={formData.no_kk} 
          onChange={handleChange} 
          placeholder="Nomor Kartu Keluarga"
          required 
        />

        <div className="grid grid-cols-2 gap-4">
          <Input label="Password" name="password" type="password" value={formData.password} onChange={handleChange} required />
          <Input label="Konfirmasi" name="password_confirm" type="password" value={formData.password_confirm} onChange={handleChange} required />
        </div>

        {/* Kolom Dinamis berdasarkan Role */}
        {formData.role === 'teacher' ? (
          <Input label="NIP / ID Pegawai" name="profile.employee_id" value={formData.profile.employee_id} onChange={handleChange} />
        ) : (
          <Input label="NISN / ID Siswa" name="profile.student_id" value={formData.profile.student_id} onChange={handleChange} />
        )}

        <Input label="Alamat" name="profile.address" value={formData.profile.address} onChange={handleChange} />

        {authError && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
            {authError}
          </div>
        )}
        {/* Baris Tanggal Lahir & Tempat Lahir */}
        <div className="grid grid-cols-2 gap-4">
          <Input
            label="Tempat Lahir"
            name="profile.place_of_birth"
            value={formData.profile.place_of_birth}
            onChange={handleChange}
            placeholder="Contoh: Jakarta"
            required
          />
          <Input
            label="Tanggal Lahir"
            name="profile.date_of_birth"
            type="date" // <--- Ini akan otomatis mengirim format YYYY-MM-DD
            value={formData.profile.date_of_birth}
            onChange={handleChange}
            required
          />
        </div>

        {/* Pilihan Jenis Kelamin */}
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">Jenis Kelamin</label>
          <select
            name="profile.gender"
            value={formData.profile.gender}
            onChange={handleChange}
            className="w-full px-3 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          >
            <option value="male">Laki-laki</option>
            <option value="female">Perempuan</option>
          </select>
        </div>


        <Button
          style={{ backgroundColor: theme.primaryColor }}
          type="submit"
          className="w-full"
          isLoading={isLoading}
        >
          Daftar Sekarang
        </Button>
      </form>

      <p className="mt-6 text-center text-sm text-gray-500">
        Sudah punya akun?{' '}
        <Link to="/login" className="text-blue-500 hover:underline">Masuk di sini</Link>
      </p>
    </div>
  )
}
