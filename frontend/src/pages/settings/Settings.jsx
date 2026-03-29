import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../../lib/api'
import Card from '../../components/ui/Card'
import Button from '../../components/ui/Button'
import Input from '../../components/ui/Input'

export default function Settings() {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState('general')
  
  // Fetch current settings
  const { data: settings, isLoading } = useQuery({
    queryKey: ['settings'],
    queryFn: () => api.get('/auth/me/'),
  })

  // Update settings mutation
  const mutation = useMutation({
    mutationFn: (data) => api.patch('/auth/me/', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] })
      alert('Pengaturan berhasil disimpan')
    },
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    const formData = new FormData(e.target)
    mutation.mutate(Object.fromEntries(formData))
  }

  const tabs = [
    { id: 'general', label: 'Umum' },
    { id: 'academic', label: 'Akademik' },
    { id: 'finance', label: 'Keuangan' },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Pengaturan</h1>
        <p className="text-gray-500">Kelola pengaturan aplikasi</p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      <Card>
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-6">
            {activeTab === 'general' && (
              <div className="space-y-4">
                <h3 className="text-lg font-medium text-gray-900">Pengaturan Umum</h3>
                <Input
                  name="school_name"
                  label="Nama Sekolah"
                  defaultValue={settings?.school_name}
                />
                <Input
                  name="address"
                  label="Alamat"
                  defaultValue={settings?.address}
                />
                <Input
                  name="phone"
                  label="Telepon"
                  defaultValue={settings?.phone}
                />
                <Input
                  name="email"
                  label="Email"
                  type="email"
                  defaultValue={settings?.email}
                />
              </div>
            )}

            {activeTab === 'academic' && (
              <div className="space-y-4">
                <h3 className="text-lg font-medium text-gray-900">Pengaturan Akademik</h3>
                <Input
                  name="academic_year"
                  label="Tahun Ajaran"
                  defaultValue={settings?.academic_year}
                />
                <Input
                  name="semester"
                  label="Semester"
                  defaultValue={settings?.semester}
                />
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    name="enable_attendance"
                    id="enable_attendance"
                    defaultChecked={settings?.enable_attendance}
                    className="rounded border-gray-300"
                  />
                  <label htmlFor="enable_attendance" className="text-sm text-gray-700">
                    Aktifkan Absensi
                  </label>
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    name="enable_scores"
                    id="enable_scores"
                    defaultChecked={settings?.enable_scores}
                    className="rounded border-gray-300"
                  />
                  <label htmlFor="enable_scores" className="text-sm text-gray-700">
                    Aktifkan Nilai
                  </label>
                </div>
              </div>
            )}

            {activeTab === 'finance' && (
              <div className="space-y-4">
                <h3 className="text-lg font-medium text-gray-900">Pengaturan Keuangan</h3>
                <Input
                  name="bank_name"
                  label="Nama Bank"
                  defaultValue={settings?.bank_name}
                />
                <Input
                  name="bank_account"
                  label="Nomor Rekening"
                  defaultValue={settings?.bank_account}
                />
                <Input
                  name="bank_account_name"
                  label="Nama Rekening"
                  defaultValue={settings?.bank_account_name}
                />
                <Input
                  name="spp_amount"
                  label="SPP Bulanan"
                  type="number"
                  defaultValue={settings?.spp_amount}
                />
              </div>
            )}

            <div className="flex justify-end">
              <Button type="submit">
                Simpan Perubahan
              </Button>
            </div>
          </form>
        )}
      </Card>
    </div>
  )
}
