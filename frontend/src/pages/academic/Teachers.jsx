import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../../lib/api'
import Card from '../../components/ui/Card'
import Button from '../../components/ui/Button'
import Input from '../../components/ui/Input'
import Select from '../../components/ui/Select'
import Modal from '../../components/ui/Modal'
import LoadingSpinner from '../../components/ui/LoadingSpinner'

export default function Teachers() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedTeacher, setSelectedTeacher] = useState(null)
  const [filters, setFilters] = useState({ search: '' })
  
  const queryClient = useQueryClient()

  // Fetch teachers
  const { data: teachers, isLoading } = useQuery({
    queryKey: ['teachers', filters],
    queryFn: () => api.get('/api/academic/teachers/', { params: filters }),
  })

  // Fetch subjects for multi-select
  const { data: subjects } = useQuery({
    queryKey: ['subjects'],
    queryFn: () => api.get('/api/academic/subjects/'),
  })

  // Create/Update mutation
  const mutation = useMutation({
    mutationFn: (data) => {
      if (selectedTeacher) {
        return api.patch(`/api/academic/teachers/${selectedTeacher.id}/`, data)
      }
      return api.post('/api/academic/teachers/', data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['teachers'] })
      setIsModalOpen(false)
      setSelectedTeacher(null)
    },
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    const formData = new FormData(e.target)
    mutation.mutate(Object.fromEntries(formData))
  }

  const subjectOptions = subjects?.results?.map(s => ({
    value: s.id,
    label: s.name,
  })) || []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Data Guru/Ustadz</h1>
          <p className="text-gray-500">Kelola data guru dan ustadz di sekolah/pesantren</p>
        </div>
        <Button onClick={() => setIsModalOpen(true)}>
          + Tambah Guru/Ustadz
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <Input
          placeholder="Cari nama, NIP..."
          value={filters.search}
          onChange={(e) => setFilters({ ...filters, search: e.target.value })}
        />
      </Card>

      {/* Table */}
      <Card noPadding>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">NIP</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nama</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Spesialisasi</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Kelas/Wali</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Aksi</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {isLoading ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12">
                    <LoadingSpinner />
                  </td>
                </tr>
              ) : teachers?.results?.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                    Tidak ada data guru/ustadz
                  </td>
                </tr>
              ) : (
                teachers?.results?.map((teacher) => (
                  <tr key={teacher.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {teacher.nip || '-'}
                    </td>
                    <td className="px-6 py-4">
                      <div>
                        <p className="text-sm font-medium text-gray-900">{teacher.name}</p>
                        <p className="text-xs text-gray-500">{teacher.email}</p>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {teacher.subjects?.map(s => s.name).join(', ') || '-'}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {teacher.class_as_wali || '-'}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        teacher.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
                      }`}>
                        {teacher.is_active ? 'Aktif' : 'Nonaktif'}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={() => {
                          setSelectedTeacher(teacher)
                          setIsModalOpen(true)
                        }}
                      >
                        Edit
                      </Button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Modal Form */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false)
          setSelectedTeacher(null)
        }}
        title={selectedTeacher ? 'Edit Guru/Ustadz' : 'Tambah Guru/Ustadz'}
        size="lg"
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="NIP"
              name="nip"
              defaultValue={selectedTeacher?.nip}
            />
            <Input
              label="Nama Lengkap"
              name="name"
              defaultValue={selectedTeacher?.name}
              required
            />
          </div>
          <Input
            label="Email"
            name="email"
            type="email"
            defaultValue={selectedTeacher?.email}
          />
          <Input
            label="No. Telepon"
            name="phone"
            defaultValue={selectedTeacher?.phone}
          />
          <Input
            label="Spesialisasi (Mapel/Kitab)"
            name="specialization"
            defaultValue={selectedTeacher?.specialization}
            placeholder="Contoh: Matematika, Al-Quran, Fiqih"
          />
          <Input
            label="Kelas Sebagai Wali Kelas"
            name="class_as_wali"
            defaultValue={selectedTeacher?.class_as_wali}
          />
          <div className="flex justify-end gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                setIsModalOpen(false)
                setSelectedTeacher(null)
              }}
            >
              Batal
            </Button>
            <Button type="submit" isLoading={mutation.isPending}>
              Simpan
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}