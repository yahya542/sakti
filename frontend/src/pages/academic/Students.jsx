import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../../lib/api'
import Card from '../../components/ui/Card'
import Button from '../../components/ui/Button'
import Input from '../../components/ui/Input'
import Select from '../../components/ui/Select'
import Modal from '../../components/ui/Modal'
import LoadingSpinner from '../../components/ui/LoadingSpinner'

export default function Students() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedStudent, setSelectedStudent] = useState(null)
  const [filters, setFilters] = useState({ search: '', class_id: '' })
  
  const queryClient = useQueryClient()

  // Fetch students
  const { data: students, isLoading } = useQuery({
    queryKey: ['students', filters],
    queryFn: () => api.get('/api/academic/students/', { params: filters }),
  })

  // Fetch classes for filter
  const { data: classes } = useQuery({
    queryKey: ['classes'],
    queryFn: () => api.get('/api/academic/classes/'),
  })

  // Create/Update mutation
  const mutation = useMutation({
    mutationFn: (data) => {
      if (selectedStudent) {
        return api.patch(`/api/academic/students/${selectedStudent.id}/`, data)
      }
      return api.post('/api/academic/students/', data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['students'] })
      setIsModalOpen(false)
      setSelectedStudent(null)
    },
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    const formData = new FormData(e.target)
    mutation.mutate(Object.fromEntries(formData))
  }

  const classOptions = classes?.results?.map(c => ({
    value: c.id,
    label: c.name,
  })) || []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Data Siswa/Santri</h1>
          <p className="text-gray-500">Kelola data siswa dan santoi di sekolah/pesantren</p>
        </div>
        <Button onClick={() => setIsModalOpen(true)}>
          + Tambah Siswa
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <div className="flex flex-wrap gap-4">
          <div className="flex-1 min-w-[200px]">
            <Input
              placeholder="Cari nama, NIS, NISN..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
            />
          </div>
          <div className="w-[200px]">
            <Select
              options={classOptions}
              value={filters.class_id}
              onChange={(e) => setFilters({ ...filters, class_id: e.target.value })}
              placeholder="Semua Kelas"
            />
          </div>
        </div>
      </Card>

      {/* Table */}
      <Card noPadding>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">NIS/NISN</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nama</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Kelas</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">No KK</th>
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
              ) : students?.results?.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                    Tidak ada data siswa
                  </td>
                </tr>
              ) : (
                students?.results?.map((student) => (
                  <tr key={student.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {student.nis} / {student.nisn}
                    </td>
                    <td className="px-6 py-4">
                      <div>
                        <p className="text-sm font-medium text-gray-900">{student.name}</p>
                        <p className="text-xs text-gray-500">{student.email}</p>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {student.class_name || '-'}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {student.no_kk || '-'}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        student.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
                      }`}>
                        {student.is_active ? 'Aktif' : 'Nonaktif'}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={() => {
                          setSelectedStudent(student)
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
          setSelectedStudent(null)
        }}
        title={selectedStudent ? 'Edit Siswa/Santri' : 'Tambah Siswa/Santri'}
        size="lg"
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="NIS"
              name="nis"
              defaultValue={selectedStudent?.nis}
              required
            />
            <Input
              label="NISN"
              name="nisn"
              defaultValue={selectedStudent?.nisn}
            />
          </div>
          <Input
            label="Nama Lengkap"
            name="name"
            defaultValue={selectedStudent?.name}
            required
          />
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Nomor KK"
              name="no_kk"
              defaultValue={selectedStudent?.no_kk}
              placeholder="untuk Smart Linking"
            />
            <Select
              label="Kelas"
              name="class_id"
              options={classOptions}
              defaultValue={selectedStudent?.class_id}
            />
          </div>
          <Input
            label="Email"
            name="email"
            type="email"
            defaultValue={selectedStudent?.email}
          />
          <Input
            label="No. Telepon"
            name="phone"
            defaultValue={selectedStudent?.phone}
          />
          <div className="flex justify-end gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                setIsModalOpen(false)
                setSelectedStudent(null)
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