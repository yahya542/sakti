import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../../lib/api'
import Card from '../../components/ui/Card'
import Button from '../../components/ui/Button'
import Input from '../../components/ui/Input'
import LoadingSpinner from '../../components/ui/LoadingSpinner'

export default function SmartLinking() {
  const queryClient = useQueryClient()
  const [filters, setFilters] = useState({ search: '', status: '' })
  const [showVerifyModal, setShowVerifyModal] = useState(false)
  const [selectedLink, setSelectedLink] = useState(null)
  
  // Fetch smart links
  const { data: linksData, isLoading } = useQuery({
    queryKey: ['smart-links', filters],
    queryFn: () => api.get('/smart-linking/links/', { params: filters }),
  })

  // Verify link mutation
  const verifyMutation = useMutation({
    mutationFn: (id) => api.post(`/smart-linking/links/${id}/verify/`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['smart-links'] })
      setShowVerifyModal(false)
      setSelectedLink(null)
      alert('Link berhasil diverifikasi')
    },
  })

  const handleVerify = (link) => {
    setSelectedLink(link)
    setShowVerifyModal(true)
  }

  const confirmVerify = () => {
    if (selectedLink) {
      verifyMutation.mutate(selectedLink.id)
    }
  }

  const getStatusColor = (status) => {
    const colors = {
      verified: 'bg-green-100 text-green-800',
      pending: 'bg-yellow-100 text-yellow-800',
      rejected: 'bg-red-100 text-red-800',
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const getStatusLabel = (status) => {
    const labels = {
      verified: 'Terverifikasi',
      pending: 'Menunggu',
      rejected: 'Ditolak',
    }
    return labels[status] || status
  }

  const getRelationLabel = (type) => {
    const labels = {
      father: 'Ayah',
      mother: 'Ibu',
      guardian: 'Wali',
      grandparent: 'Kakek/Nenek',
      sibling: 'Kakak/Adik',
      other: 'Lainnya',
    }
    return labels[type] || type
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Smart Linking</h1>
          <p className="text-gray-500">Kelola hubungan wali murid dan siswa/santri</p>
        </div>
      </div>

      {/* Info Card */}
      <Card className="bg-blue-50 border-blue-200">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <h3 className="text-sm font-medium text-blue-800">Cara Kerja Smart Linking</h3>
            <p className="text-sm text-blue-700 mt-1">
              Sistem akan secara otomatis menghubungkan akun wali murid dengan siswa berdasarkan No. KK (Nomor Kartu Keluarga).
              Wali murid dapat melihat data akademik dan keuangan anak mereka setelah link diverifikasi.
            </p>
          </div>
        </div>
      </Card>

      {/* Filters */}
      <Card>
        <div className="flex flex-wrap gap-4">
          <div className="flex-1 min-w-[200px]">
            <Input
              placeholder="Cari siswa atau wali..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
            />
          </div>
          <div className="w-[200px]">
            <select
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Semua Status</option>
              <option value="pending">Menunggu</option>
              <option value="verified">Terverifikasi</option>
              <option value="rejected">Ditolak</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Table */}
      <Card>
        {isLoading ? (
          <LoadingSpinner />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4">Wali Murid</th>
                  <th className="text-left py-3 px-4">Siswa/Santri</th>
                  <th className="text-left py-3 px-4">Hubungan</th>
                  <th className="text-left py-3 px-4">No. KK</th>
                  <th className="text-left py-3 px-4">Status</th>
                  <th className="text-left py-3 px-4">Aksi</th>
                </tr>
              </thead>
              <tbody>
                {linksData?.results?.map((link) => (
                  <tr key={link.id} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4">
                      <div>
                        <p className="font-medium">{link.parent?.name}</p>
                        <p className="text-sm text-gray-500">{link.parent?.phone}</p>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <div>
                        <p className="font-medium">{link.student?.name}</p>
                        <p className="text-sm text-gray-500">{link.student?.nis}</p>
                      </div>
                    </td>
                    <td className="py-3 px-4">{getRelationLabel(link.relation_type)}</td>
                    <td className="py-3 px-4 font-mono text-sm">{link.no_kk}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-1 rounded text-sm ${getStatusColor(link.status)}`}>
                        {getStatusLabel(link.status)}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      {link.status === 'pending' && (
                        <div className="flex gap-2">
                          <Button 
                            variant="secondary"
                            size="sm"
                            onClick={() => handleVerify(link)}
                          >
                            Verifikasi
                          </Button>
                        </div>
                      )}
                      {link.status === 'verified' && (
                        <span className="text-sm text-gray-500">
                          Sejak {link.verified_at}
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* Verify Modal */}
      {showVerifyModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Verifikasi Link
            </h3>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-500">Wali Murid</p>
                <p className="font-medium">{selectedLink?.parent?.name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Siswa/Santri</p>
                <p className="font-medium">{selectedLink?.student?.name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Hubungan</p>
                <p className="font-medium">{getRelationLabel(selectedLink?.relation_type)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">No. KK</p>
                <p className="font-medium font-mono">{selectedLink?.no_kk}</p>
              </div>
            </div>
            <div className="flex justify-end gap-2 mt-6">
              <Button 
                variant="secondary" 
                onClick={() => {
                  setShowVerifyModal(false)
                  setSelectedLink(null)
                }}
              >
                Batal
              </Button>
              <Button onClick={confirmVerify}>
                Verifikasi
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
