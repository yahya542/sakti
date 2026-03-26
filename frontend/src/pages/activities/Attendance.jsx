import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../../lib/api'
import Card from '../../components/ui/Card'
import Button from '../../components/ui/Button'
import Input from '../../components/ui/Input'
import Select from '../../components/ui/Select'
import Modal from '../../components/ui/Modal'
import LoadingSpinner from '../../components/ui/LoadingSpinner'

export default function Attendance() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedAttendance, setSelectedAttendance] = useState(null)
  const [filters, setFilters] = useState({ search: '', class_id: '', date: '' })
  
  const queryClient = useQueryClient()

  // Fetch attendance records
  const { data: attendanceData, isLoading } = useQuery({
    queryKey: ['attendance', filters],
    queryFn: () => api.get('/api/activities/attendance/', { params: filters }),
  })

  // Fetch classes for filter
  const { data: classes } = useQuery({
    queryKey: ['classes'],
    queryFn: () => api.get('/api/academic/classes/'),
  })

  // Create/Update mutation
  const mutation = useMutation({
    mutationFn: (data) => {
      if (selectedAttendance) {
        return api.patch(`/api/activities/attendance/${selectedAttendance.id}/`, data)
      }
      return api.post('/api/activities/attendance/', data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['attendance'] })
      setIsModalOpen(false)
      setSelectedAttendance(null)
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
          <h1 className="text-2xl font-bold text-gray-900">Absensi</h1>
          <p className="text-gray-500">Kelola absensi siswa/santri</p>
        </div>
        <Button onClick={() => setIsModalOpen(true)}>
          + Tambah Absensi
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <div className="flex flex-wrap gap-4">
          <div className="flex-1 min-w-[200px]">
            <Input
              placeholder="Cari siswa..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
            />
          </div>
          <div className="w-[200px]">
            <Select
              options={classOptions}
              value={filters.class_id}
              onChange={(e) => setFilters({ ...filters, class_id: e.target.value })}
              placeholder="Pilih Kelas"
            />
          </div>
          <div className="w-[200px]">
            <Input
              type="date"
              value={filters.date}
              onChange={(e) => setFilters({ ...filters, date: e.target.value })}
            />
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
                  <th className="text-left py-3 px-4">Tanggal</th>
                  <th className="text-left py-3 px-4">Siswa</th>
                  <th className="text-left py-3 px-4">Kelas</th>
                  <th className="text-left py-3 px-4">Status</th>
                  <th className="text-left py-3 px-4">Keterangan</th>
                  <th className="text-left py-3 px-4">Aksi</th>
                </tr>
              </thead>
              <tbody>
                {attendanceData?.results?.map((record) => (
                  <tr key={record.id} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4">{record.date}</td>
                    <td className="py-3 px-4">{record.student?.name}</td>
                    <td className="py-3 px-4">{record.student?.class?.name}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-1 rounded text-sm ${
                        record.status === 'present' ? 'bg-green-100 text-green-800' :
                        record.status === 'absent' ? 'bg-red-100 text-red-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {record.status === 'present' ? 'Hadir' : 
                         record.status === 'absent' ? 'Tidak Hadir' : 'Izin'}
                      </span>
                    </td>
                    <td className="py-3 px-4">{record.notes || '-'}</td>
                    <td className="py-3 px-4">
                      <Button 
                        variant="secondary"
                        size="sm"
                        onClick={() => {
                          setSelectedAttendance(record)
                          setIsModalOpen(true)
                        }}
                      >
                        Edit
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false)
          setSelectedAttendance(null)
        }}
        title={selectedAttendance ? 'Edit Absensi' : 'Tambah Absensi'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            name="student"
            label="Siswa"
            placeholder="Nama siswa"
            defaultValue={selectedAttendance?.student?.name}
            required
          />
          <Input
            name="date"
            label="Tanggal"
            type="date"
            defaultValue={selectedAttendance?.date}
            required
          />
          <Select
            name="status"
            label="Status"
            options={[
              { value: 'present', label: 'Hadir' },
              { value: 'absent', label: 'Tidak Hadir' },
              { value: 'excused', label: 'Izin' },
            ]}
            defaultValue={selectedAttendance?.status}
            required
          />
          <Input
            name="notes"
            label="Keterangan"
            placeholder="Keterangan absensi"
            defaultValue={selectedAttendance?.notes}
          />
          <div className="flex justify-end gap-2">
            <Button type="button" variant="secondary" onClick={() => setIsModalOpen(false)}>
              Batal
            </Button>
            <Button type="submit">
              Simpan
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
