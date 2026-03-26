import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../../lib/api'
import Card from '../../components/ui/Card'
import Button from '../../components/ui/Button'
import Input from '../../components/ui/Input'
import LoadingSpinner from '../../components/ui/LoadingSpinner'

export default function TenantSettings() {
  const queryClient = useQueryClient()
  
  // Fetch current tenant settings
  const { data: tenant, isLoading } = useQuery({
    queryKey: ['tenant'],
    queryFn: () => api.get('/api/tenants/current/'),
  })

  // Update tenant mutation
  const mutation = useMutation({
    mutationFn: (data) => api.patch('/api/tenants/current/', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tenant'] })
      alert('Pengaturan berhasil disimpan')
    },
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    const formData = new FormData(e.target)
    mutation.mutate(Object.fromEntries(formData))
  }

  if (isLoading) {
    return <LoadingSpinner />
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Pengaturan Tenant</h1>
        <p className="text-gray-500">Kelola pengaturan tenant/sektor</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Basic Info */}
        <Card>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Informasi Dasar</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              name="name"
              label="Nama Tenant"
              defaultValue={tenant?.name}
              required
            />
            <Input
              name="slug"
              label="Slug"
              defaultValue={tenant?.slug}
              disabled
            />
            <Input
              name="code"
              label="Kode Tenant"
              defaultValue={tenant?.code}
              disabled
            />
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <div className="flex items-center gap-2">
                <span className={`px-2 py-1 rounded text-sm ${
                  tenant?.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {tenant?.is_active ? 'Aktif' : 'Nonaktif'}
                </span>
              </div>
            </div>
            <Button type="submit">
              Simpan
            </Button>
          </form>
        </Card>

        {/* Contact Info */}
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
              name="website"
              label="Website"
              defaultValue={tenant?.website}
            />
            <Button type="submit">
              Simpan
            </Button>
          </form>
        </Card>

        {/* Subscription */}
        <Card>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Informasi Langganan</h3>
          <div className="space-y-4">
            <div>
              <p className="text-sm text-gray-500">Plan</p>
              <p className="font-medium">{tenant?.subscription?.plan || 'Free'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Mulai Langganan</p>
              <p className="font-medium">{tenant?.subscription?.start_date || '-'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Berakhir</p>
              <p className="font-medium">{tenant?.subscription?.end_date || '-'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Pengguna</p>
              <p className="font-medium">
                {tenant?.subscription?.used_users} / {tenant?.subscription?.max_users || '∞'}
              </p>
            </div>
          </div>
        </Card>

        {/* Features */}
        <Card>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Fitur Aktif</h3>
          <div className="space-y-2">
            {tenant?.features?.map((feature) => (
              <div key={feature.id} className="flex items-center justify-between py-2 border-b">
                <span className="text-gray-700">{feature.name}</span>
                <span className={`px-2 py-1 rounded text-xs ${
                  feature.enabled ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                }`}>
                  {feature.enabled ? 'Aktif' : 'Nonaktif'}
                </span>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  )
}