import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../../lib/api'
import Card from '../../components/ui/Card'
import Button from '../../components/ui/Button'
import Input from '../../components/ui/Input'
import LoadingSpinner from '../../components/ui/LoadingSpinner'

export default function TenantSettings() {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState('branding')
  
  // Fetch current tenant settings
  const { data: tenant, isLoading } = useQuery({
    queryKey: ['tenant'],
    queryFn: () => api.get('/tenants/current/'),
  })

  // Update tenant mutation
  const mutation = useMutation({
    mutationFn: (formData) => api.patch('/tenants/current/', formData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tenant'] })
      alert('Pengaturan berhasil disimpan')
    },
    onError: (error) => {
      alert('Gagal menyimpan: ' + (error.response?.data?.message || error.message))
    }
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    const formData = new FormData(e.target)
    
    // Remove empty values
    for (const [key, value] of formData.entries()) {
      if (!value) {
        formData.delete(key)
      }
    }
    
    mutation.mutate(formData)
  }

  const tabs = [
    { id: 'branding', label: 'Branding' },
    { id: 'info', label: 'Informasi' },
    { id: 'theme', label: 'Warna Tema' },
  ]

  if (isLoading) {
    return <LoadingSpinner />
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Pengaturan Tenant</h1>
        <p className="text-gray-500">Kelola tampilan dan konfigurasi tenant</p>
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

      {/* Branding Tab */}
      {activeTab === 'branding' && (
        <Card>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Branding & Logo</h3>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Logo */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Logo
                </label>
                {tenant?.logo && (
                  <img 
                    src={tenant.logo} 
                    alt="Logo" 
                    className="w-32 h-32 object-contain mb-2 border rounded"
                  />
                )}
                <input
                  type="file"
                  name="logo"
                  accept="image/*"
                  className="block w-full text-sm text-gray-500
                    file:mr-4 file:py-2 file:px-4
                    file:rounded-full file:border-0
                    file:text-sm file:font-semibold
                    file:bg-blue-50 file:text-blue-700
                    hover:file:bg-blue-100"
                />
              </div>
              
              {/* Favicon */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Favicon
                </label>
                {tenant?.favicon && (
                  <img 
                    src={tenant.favicon} 
                    alt="Favicon" 
                    className="w-16 h-16 object-contain mb-2 border rounded"
                  />
                )}
                <input
                  type="file"
                  name="favicon"
                  accept="image/*"
                  className="block w-full text-sm text-gray-500
                    file:mr-4 file:py-2 file:px-4
                    file:rounded-full file:border-0
                    file:text-sm file:font-semibold
                    file:bg-blue-50 file:text-blue-700
                    hover:file:bg-blue-100"
                />
              </div>
            </div>
            
            <Input
              name="name"
              label="Nama Tenant"
              defaultValue={tenant?.name}
              required
            />
            
            <Input
              name="sub_brand_name"
              label="Nama Sub-brand"
              defaultValue={tenant?.sub_brand_name}
              placeholder="Nama alternatif yang ditampilkan di dashboard"
            />
            
            <div className="flex items-center gap-2">
              <span className={`px-2 py-1 rounded text-sm ${
                tenant?.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                {tenant?.is_active ? 'Aktif' : 'Nonaktif'}
              </span>
            </div>
            
            <Button type="submit"
             style={{ backgroundColor: tenant?.primary_color || '#5dea5d' }}
            >
              Simpan Perubahan
            </Button>
          </form>
        </Card>
      )}

      {/* Info Tab */}
      {activeTab === 'info' && (
        <Card>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Informasi Kontak</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              name="address"
              label="Alamat"
              defaultValue={tenant?.address}
            />
            <Input
              name="phone"
              label="Telepon"
              defaultValue={tenant?.phone}
            />
            <Input
              name="email"
              label="Email"
              type="email"
              defaultValue={tenant?.email}
            />
            <Input
              name="custom_domain"
              label="Custom Domain"
              placeholder="contoh: sakti.uim.ac.id"
              defaultValue={tenant?.custom_domain}
            />
            
            <div className="pt-4 border-t">
              <h4 className="text-md font-medium text-gray-900 mb-4">Informasi Langganan</h4>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-500">Plan</p>
                  <p className="font-medium">{tenant?.plan || 'Free'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Kode Instansi</p>
                  <p className="font-medium">{tenant?.kode_instansi || '-'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Dibayar Sampai</p>
                  <p className="font-medium">{tenant?.paid_until || '-'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">SPP Default</p>
                  <p className="font-medium">Rp {tenant?.spp_amount?.toLocaleString('id-ID') || '500.000'}</p>
                </div>
              </div>
            </div>
            
            <Button type="submit"  
              style={{ backgroundColor: tenant?.primary_color || '#5dea5d' }}
            >
              Simpan Perubahan
            </Button>
          </form>
        </Card>
      )}

      {/* Theme Tab */}
      {activeTab === 'theme' && (
        <Card>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Warna Tema</h3>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Warna Primer
                </label>
                <div className="flex gap-2">
                  <input
                    type="color"
                    name="primary_color"
                    defaultValue={tenant?.primary_color || '#3B82F6'}
                    className="w-12 h-10 rounded cursor-pointer"
                  />
                  <input
                    type="text"
                    name="primary_color"
                    defaultValue={tenant?.primary_color || '#3B82F6'}
                    className="flex-1 border rounded px-3 py-2"
                    placeholder="#3B82F6"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Warna Sekunder
                </label>
                <div className="flex gap-2">
                  <input
                    type="color"
                    name="secondary_color"
                    defaultValue={tenant?.secondary_color || '#8B5CF6'}
                    className="w-12 h-10 rounded cursor-pointer"
                  />
                  <input
                    type="text"
                    name="secondary_color"
                    defaultValue={tenant?.secondary_color || '#8B5CF6'}
                    className="flex-1 border rounded px-3 py-2"
                    placeholder="#8B5CF6"
                  />
                </div>
              </div>
            </div>
            
            {/* Preview */}
            <div className="p-4 border rounded-lg">
              <p className="text-sm text-gray-500 mb-2">Preview:</p>
              <div className="flex gap-4">
                <span 
                  className="px-4 py-2 rounded text-white text-sm font-medium"
                  style={{ backgroundColor: tenant?.primary_color || '#3B82F6' }}
                >
                  Primer
                </span>
                <span 
                  className="px-4 py-2 rounded text-white text-sm font-medium"
                  style={{ backgroundColor: tenant?.secondary_color || '#8B5CF6' }}
                >
                  Sekunder
                </span>
              </div>
            </div>
            
            <Button type="submit"
              style={{ backgroundColor: tenant?.primary_color || '#5dea5d' }}
             >
              Simpan Perubahan
            </Button>
          </form>
        </Card>
      )}
    </div>
  )
}