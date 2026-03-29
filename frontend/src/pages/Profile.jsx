import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuthStore } from '../store/authStore'
import { useTenantStore } from '../store/tenantStore'
import api from '../lib/api'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Input from '../components/ui/Input'
import LoadingSpinner from '../components/ui/LoadingSpinner'

// Icons
const UserIcon = () => (
  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
  </svg>
)

const MailIcon = () => (
  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
  </svg>
)

const PhoneIcon = () => (
  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
  </svg>
)

const LockIcon = () => (
  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
  </svg>
)

const SaveIcon = () => (
  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
  </svg>
)

export default function Profile() {
  const { user, updateUser } = useAuthStore()
  const { theme } = useTenantStore()
  const queryClient = useQueryClient()
  
  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    email: user?.email || '',
    phone: user?.phone || '',
  })
  
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  })

  // Update profile mutation
  const profileMutation = useMutation({
    mutationFn: (data) => api.patch('/auth/me/', data),
    onSuccess: (data) => {
      updateUser(data.data)
      queryClient.invalidateQueries({ queryKey: ['user'] })
      setIsEditing(false)
      alert('Profil berhasil diperbarui!')
    },
    onError: (error) => {
      alert('Gagal memperbarui profil: ' + (error.response?.data?.message || error.message))
    }
  })

  // Change password mutation
  const passwordMutation = useMutation({
    mutationFn: (data) => api.post('/auth/me/change_password/', data),
    onSuccess: () => {
      setPasswordData({ current_password: '', new_password: '', confirm_password: '' })
      alert('Kata sandi berhasil diubah!')
    },
    onError: (error) => {
      alert('Gagal mengubah kata sandi: ' + (error.response?.data?.message || error.message))
    }
  })

  const handleProfileSubmit = (e) => {
    e.preventDefault()
    profileMutation.mutate(formData)
  }

  const handlePasswordSubmit = (e) => {
    e.preventDefault()
    
    if (passwordData.new_password !== passwordData.confirm_password) {
      alert('Kata sandi baru tidak cocok!')
      return
    }
    
    if (passwordData.new_password.length < 8) {
      alert('Kata sandi minimal 8 karakter!')
      return
    }
    
    passwordMutation.mutate({
      current_password: passwordData.current_password,
      new_password: passwordData.new_password,
    })
  }

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

  const isLoading = profileMutation.isPending || passwordMutation.isPending

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Profil Saya</h1>
        <p className="text-gray-500">Kelola informasi profil dan kata sandi Anda</p>
      </div>

      {/* Profile Information Card */}
      <Card title="Informasi Profil">
        <form onSubmit={handleProfileSubmit} className="space-y-6">
          {/* Avatar Display */}
          <div className="flex items-center gap-4 pb-6 border-b border-gray-100">
            <div 
              className="w-20 h-20 rounded-full flex items-center justify-center text-white text-2xl font-bold"
              style={{ backgroundColor: theme.primaryColor }}
            >
              {user?.first_name?.[0] || 'U'}
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                {user?.full_name || `${user?.first_name} ${user?.last_name}`}
              </h3>
              <p className="text-sm text-gray-500">{getRoleLabel(user?.role)}</p>
              <p className="text-xs text-gray-400">
                Bergabung sejak: {user?.date_joined ? new Date(user.date_joined).toLocaleDateString('id-ID') : '-'}
              </p>
            </div>
          </div>

          {/* Form Fields */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nama Depan
              </label>
              <Input
                value={formData.first_name}
                onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                disabled={!isEditing}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nama Belakang
              </label>
              <Input
                value={formData.last_name}
                onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                disabled={!isEditing}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <MailIcon />
                </div>
                <Input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  disabled={!isEditing}
                  className="pl-10"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                No. Telepon
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <PhoneIcon />
                </div>
                <Input
                  type="tel"
                  value={formData.phone || ''}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  disabled={!isEditing}
                  className="pl-10"
                  placeholder="0821xxxxxxx"
                />
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end gap-3 pt-4 border-t border-gray-100">
            {isEditing ? (
              <>
                <Button 
                  type="button" 
                  variant="secondary"
                  onClick={() => setIsEditing(false)}
                  disabled={isLoading}
                >
                  Batal
                </Button>
                <Button 
                  type="submit"
                  disabled={isLoading}
                >
                  {isLoading ? <LoadingSpinner /> : 'Simpan Perubahan'}
                </Button>
              </>
            ) : (
              <Button 
                type="button" 
                onClick={() => setIsEditing(true)}
              >
                Edit Profil
              </Button>
            )}
          </div>
        </form>
      </Card>

      {/* Change Password Card */}
      <Card title="Ubah Kata Sandi">
        <form onSubmit={handlePasswordSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Kata Sandi Lama
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <LockIcon />
                </div>
                <Input
                  type="password"
                  value={passwordData.current_password}
                  onChange={(e) => setPasswordData({ ...passwordData, current_password: e.target.value })}
                  className="pl-10"
                  placeholder="Masukkan kata sandi lama"
                  required
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Kata Sandi Baru
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <LockIcon />
                </div>
                <Input
                  type="password"
                  value={passwordData.new_password}
                  onChange={(e) => setPasswordData({ ...passwordData, new_password: e.target.value })}
                  className="pl-10"
                  placeholder="Min. 8 karakter"
                  required
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Konfirmasi Kata Sandi
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <LockIcon />
                </div>
                <Input
                  type="password"
                  value={passwordData.confirm_password}
                  onChange={(e) => setPasswordData({ ...passwordData, confirm_password: e.target.value })}
                  className="pl-10"
                  placeholder="Ulangi kata sandi baru"
                  required
                />
              </div>
            </div>
          </div>

          <div className="flex justify-end pt-4 border-t border-gray-100">
            <Button 
              type="submit"
              disabled={isLoading || !passwordData.current_password || !passwordData.new_password}
            >
              {isLoading ? <LoadingSpinner /> : 'Ubah Kata Sandi'}
            </Button>
          </div>
        </form>
      </Card>

      {/* Account Info Card */}
      <Card title="Informasi Akun">
        <div className="space-y-4">
          <div className="flex items-center justify-between py-3 border-b border-gray-100">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gray-100 rounded-lg">
                <UserIcon />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">Role</p>
                <p className="text-xs text-gray-500">Peran pengguna dalam sistem</p>
              </div>
            </div>
            <span className="px-3 py-1 bg-blue-100 text-blue-700 text-sm rounded-full">
              {getRoleLabel(user?.role)}
            </span>
          </div>
          
          <div className="flex items-center justify-between py-3 border-b border-gray-100">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gray-100 rounded-lg">
                <UserIcon />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">Status Akun</p>
                <p className="text-xs text-gray-500">Status keaktifan akun</p>
              </div>
            </div>
            <span className={`px-3 py-1 rounded-full text-sm ${user?.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
              {user?.is_active ? 'Aktif' : 'Nonaktif'}
            </span>
          </div>
          
          {user?.tenant && (
            <div className="flex items-center justify-between py-3">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-gray-100 rounded-lg">
                  <UserIcon />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">Institution</p>
                  <p className="text-xs text-gray-500">Sekolah/Pesantren</p>
                </div>
              </div>
              <span className="text-sm text-gray-600">
                {user.tenant}
              </span>
            </div>
          )}
        </div>
      </Card>
    </div>
  )
}