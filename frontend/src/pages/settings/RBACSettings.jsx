import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../../lib/api'
import Card from '../../components/ui/Card'
import Button from '../../components/ui/Button'
import LoadingSpinner from '../../components/ui/LoadingSpinner'

const ROLE_LABELS = {
  super_admin: 'Super Admin',
  admin_school: 'Admin Sekolah',
  teacher: 'Guru/Ustadz',
  student: 'Siswa/Santri',
  parent: 'Wali Murid',
}

const DEFAULT_PERMISSIONS = {
  super_admin: [
    'tenant:manage', 'user:create', 'user:read', 'user:update', 'user:delete',
    'academic:manage', 'finance:manage', 'activities:manage', 'rbac:manage'
  ],
  admin_school: [
    'user:create', 'user:read', 'user:update',
    'academic:manage', 'finance:manage', 'activities:manage'
  ],
  teacher: [
    'academic:read', 'activities:create', 'activities:read', 'activities:update'
  ],
  student: [
    'academic:read', 'activities:read', 'finance:read'
  ],
  parent: [
    'student:read', 'activities:read', 'finance:read'
  ],
}

export default function RBACSettings() {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState('roles')
  const [selectedRole, setSelectedRole] = useState(null)
  const [rolePermissions, setRolePermissions] = useState({})

  // Fetch permissions
  const { data: permissions, isLoading: permissionsLoading } = useQuery({
    queryKey: ['permissions'],
    queryFn: () => api.get('/rbac/permissions/'),
  })

  // Fetch role permissions
  const { data: roleData, isLoading: roleLoading } = useQuery({
    queryKey: ['rolePermissions', selectedRole],
    queryFn: () => api.get(`/rbac/permissions/role_permissions/?role=${selectedRole}`),
    enabled: !!selectedRole
  })

  // Update role permissions mutation
  const updateMutation = useMutation({
    mutationFn: (data) => api.post('/rbac/permissions/update_role/', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rolePermissions'] })
      alert('Hak akses berhasil diperbarui')
    },
    onError: (error) => {
      alert('Gagal memperbarui: ' + (error.response?.data?.message || error.message))
    }
  })

  const tabs = [
    { id: 'roles', label: 'Kelola Roles' },
    { id: 'permissions', label: 'Kelola Permissions' },
  ]

  const roles = Object.keys(ROLE_LABELS)

  const handleRoleSelect = (role) => {
    setSelectedRole(role)
    // Set default permissions if not already set
    if (!rolePermissions[role]) {
      setRolePermissions(prev => ({
        ...prev,
        [role]: DEFAULT_PERMISSIONS[role] || []
      }))
    }
  }

  const handlePermissionToggle = (role, permission) => {
    setRolePermissions(prev => {
      const current = prev[role] || []
      const updated = current.includes(permission)
        ? current.filter(p => p !== permission)
        : [...current, permission]
      return { ...prev, [role]: updated }
    })
  }

  const handleSavePermissions = () => {
    updateMutation.mutate({
      role: selectedRole,
      permissions: rolePermissions[selectedRole] || []
    })
  }

  if (permissionsLoading || roleLoading) {
    return <LoadingSpinner />
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Pengaturan RBAC</h1>
        <p className="text-gray-500">Kelola Role-Based Access Control</p>
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

      {/* Roles Tab */}
      {activeTab === 'roles' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Role List */}
          <Card>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Daftar Role</h3>
            <div className="space-y-2">
              {roles.map((role) => (
                <button
                  key={role}
                  onClick={() => handleRoleSelect(role)}
                  className={`w-full text-left px-4 py-3 rounded-lg border ${
                    selectedRole === role
                      ? 'border-blue-500 bg-blue-50 text-blue-700'
                      : 'border-gray-200 hover:bg-gray-50'
                  }`}
                >
                  <div className="font-medium">{ROLE_LABELS[role]}</div>
                  <div className="text-sm text-gray-500">
                    {DEFAULT_PERMISSIONS[role]?.length || 0} permissions
                  </div>
                </button>
              ))}
            </div>
          </Card>

          {/* Role Permissions */}
          <Card className="md:col-span-2">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Permissions untuk {selectedRole ? ROLE_LABELS[selectedRole] : 'Pilih Role'}
            </h3>
            
            {!selectedRole ? (
              <div className="text-center py-8 text-gray-500">
                Pilih role di sebelah kiri untuk melihat dan mengedit permissions
              </div>
            ) : (
              <div className="space-y-4">
                {roleData?.permissions ? (
                  <div className="space-y-2">
                    {roleData.permissions.map((perm) => (
                      <div
                        key={perm.code}
                        className="flex items-center justify-between p-3 border rounded-lg"
                      >
                        <div>
                          <div className="font-medium">{perm.name}</div>
                          <div className="text-sm text-gray-500">{perm.code}</div>
                        </div>
                        <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-sm">
                          Aktif
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-4 text-gray-500">
                    Tidak ada permissions untuk role ini
                  </div>
                )}
              </div>
            )}
          </Card>
        </div>
      )}

      {/* Permissions Tab */}
      {activeTab === 'permissions' && (
        <Card>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Semua Permissions</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Kode
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Nama
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Deskripsi
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {permissions?.results?.map((perm) => (
                  <tr key={perm.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <code className="text-sm bg-gray-100 px-2 py-1 rounded">
                        {perm.code}
                      </code>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap font-medium">
                      {perm.name}
                    </td>
                    <td className="px-6 py-4 text-gray-500">
                      {perm.description || '-'}
                    </td>
                  </tr>
                )) || (
                  <tr>
                    <td colSpan={3} className="px-6 py-4 text-center text-gray-500">
                      Tidak ada data permissions
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  )
}