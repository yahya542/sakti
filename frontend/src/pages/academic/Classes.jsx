import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../../lib/api'
import Card from '../../components/ui/Card'
import Button from '../../components/ui/Button'
import Input from '../../components/ui/Input'
import Select from '../../components/ui/Select'
import Modal from '../../components/ui/Modal'
import LoadingSpinner from '../../components/ui/LoadingSpinner'

export default function Classes() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedClass, setSelectedClass] = useState(null)
  
  const queryClient = useQueryClient()

  // Fetch classes
  const { data: classes, isLoading } = useQuery({
    queryKey: ['classes'],
    queryFn: () => api.get('/academic/classrooms/'),
  })

  // Fetch teachers for walikelas selection
  const { data: teachers } = useQuery({
    queryKey: ['teachers'],
    queryFn: () => api.get('/academic/teachers/'),
  })

  // Create/Update mutation
  const mutation = useMutation({
    mutationFn: (data) => {
      if (selectedClass) {
        return api.patch(`/academic/classrooms/${selectedClass.id}/`, data)
      }
      return api.post('/academic/classrooms/', data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['classes'] })
      setIsModalOpen(false)
      setSelectedClass(null)
    },
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    const formData = new FormData(e.target)
    mutation.mutate(Object.fromEntries(formData))
  }

  const teacherOptions = teachers?.results?.map(t => ({
    value: t.id,
    label: t.name,
  })) || []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Data Kelas/Madrasah</h1>
          <p className="text-gray-500">Kelola kelas dan madrasah di sekolah/pesantren</p>
        </div>
        <Button onClick={() => setIsModalOpen(true)}>
          + Tambah Kelas
        </Button>
      </div>

      {/* Classes Grid */}
      {isLoading ? (
        <div className="flex justify-center py-12">
          <LoadingSpinner />
        </div>
      ) : classes?.results?.length === 0 ? (
        <Card>
          <div className="text-center py-12 text-gray-500">
            Tidak ada data kelas
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {classes?.results?.map((cls) => (
            <Card key={cls.id} className="hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{cls.name}</h3>
                  <p className="text-sm text-gray-500">{cls.level || 'Kelas'}</p>
                </div>
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={() => {
                    setSelectedClass(cls)
                    setIsModalOpen(true)
                  }}
                >
                  Edit
                </Button>
              </div>
              <div className="mt-4 pt-4 border-t border-gray-100">
                <div className="flex items-center text-sm text-gray-600">
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  <span>Wali Kelas: {cls.wali_kelas || '-'}</span>
                </div>
                <div className="flex items-center mt-2 text-sm text-gray-600">
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                  <span>Siswa: {cls.student_count || 0}</span>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Modal Form */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false)
          setSelectedClass(null)
        }}
        title={selectedClass ? 'Edit Kelas' : 'Tambah Kelas'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Nama Kelas"
            name="name"
            defaultValue={selectedClass?.name}
            placeholder="Contoh: Kelas 7A, Madrasah Tsania"
            required
          />
          <Input
            label="Tingkat/Level"
            name="level"
            defaultValue={selectedClass?.level}
            placeholder="Contoh: VII, VIII, IX"
          />
          <Select
            label="Wali Kelas/Ustadz Pendamping"
            name="wali_kelas_id"
            options={teacherOptions}
            defaultValue={selectedClass?.wali_kelas_id}
          />
          <div className="flex justify-end gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                setIsModalOpen(false)
                setSelectedClass(null)
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