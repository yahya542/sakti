import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../../lib/api'
import Card from '../../components/ui/Card'
import Button from '../../components/ui/Button'
import Input from '../../components/ui/Input'
import Select from '../../components/ui/Select'
import Modal from '../../components/ui/Modal'
import LoadingSpinner from '../../components/ui/LoadingSpinner'

export default function Subjects() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedSubject, setSelectedSubject] = useState(null)
  const [filters, setFilters] = useState({ search: '', type: '' })
  
  const queryClient = useQueryClient()

  // Fetch subjects
  const { data: subjects, isLoading } = useQuery({
    queryKey: ['subjects', filters],
    queryFn: () => api.get('/academic/subjects/', { params: filters }),
  })

  // Create/Update mutation
  const mutation = useMutation({
    mutationFn: (data) => {
      if (selectedSubject) {
        return api.patch(`/academic/subjects/${selectedSubject.id}/`, data)
      }
      return api.post('/academic/subjects/', data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subjects'] })
      setIsModalOpen(false)
      setSelectedSubject(null)
    },
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    const formData = new FormData(e.target)
    mutation.mutate(Object.fromEntries(formData))
  }

  const subjectTypeOptions = [
    { value: 'mapel', label: 'Mata Pelajaran (Umum)' },
    { value: 'kitab', label: 'Kitab (Pesantren)' },
    { value: 'diniyah', label: 'Diniyah' },
  ]

  const categoryOptions = [
    { value: 'umum', label: 'Umum' },
    { value: 'agama', label: 'Agama' },
    { value: 'bahasa', label: 'Bahasa' },
    { value: 'seni', label: 'Seni' },
    { value: 'olraga', label: 'Olahraga' },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Data Mapel/Kitab</h1>
          <p className="text-gray-500">Kelola mata pelajaran dan kitab di sekolah/pesantren</p>
        </div>
        <Button onClick={() => setIsModalOpen(true)}>
          + Tambah Mapel/Kitab
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <div className="flex flex-wrap gap-4">
          <div className="flex-1 min-w-[200px]">
            <Input
              placeholder="Cari nama mapel/kitab..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
            />
          </div>
          <div className="w-[200px]">
            <Select
              options={subjectTypeOptions}
              value={filters.type}
              onChange={(e) => setFilters({ ...filters, type: e.target.value })}
              placeholder="Semua Tipe"
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
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Kode</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nama</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tipe</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Kategori</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">KKM</th>
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
              ) : subjects?.results?.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                    Tidak ada data mapel/kitab
                  </td>
                </tr>
              ) : (
                subjects?.results?.map((subject) => (
                  <tr key={subject.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm text-gray-900 font-mono">
                      {subject.code}
                    </td>
                    <td className="px-6 py-4">
                      <div>
                        <p className="text-sm font-medium text-gray-900">{subject.name}</p>
                        <p className="text-xs text-gray-500">{subject.name_ar || '-'}</p>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        subject.type === 'kitab' ? 'bg-purple-100 text-purple-800' :
                        subject.type === 'diniyah' ? 'bg-blue-100 text-blue-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {subject.type === 'mapel' ? 'Mapel' : 
                         subject.type === 'kitab' ? 'Kitab' : 'Diniyah'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {subject.category || '-'}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {subject.kkm || '-'}
                    </td>
                    <td className="px-6 py-4">
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={() => {
                          setSelectedSubject(subject)
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
          setSelectedSubject(null)
        }}
        title={selectedSubject ? 'Edit Mapel/Kitab' : 'Tambah Mapel/Kitab'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Kode"
              name="code"
              defaultValue={selectedSubject?.code}
              placeholder="Contoh: MTK, B.ING"
              required
            />
            <Input
              label="Nama"
              name="name"
              defaultValue={selectedSubject?.name}
              placeholder="Contoh: Matematika"
              required
            />
          </div>
          <Input
            label="Nama Arab"
            name="name_ar"
            defaultValue={selectedSubject?.name_ar}
            placeholder="Nama dalam bahasa arab"
            dir="rtl"
          />
          <div className="grid grid-cols-2 gap-4">
            <Select
              label="Tipe"
              name="type"
              options={subjectTypeOptions}
              defaultValue={selectedSubject?.type || 'mapel'}
            />
            <Select
              label="Kategori"
              name="category"
              options={categoryOptions}
              defaultValue={selectedSubject?.category}
            />
          </div>
          <Input
            label="KKM (Kriteria Ketuntasan Minimal)"
            name="kkm"
            type="number"
            defaultValue={selectedSubject?.kkm || 75}
          />
          <div className="flex justify-end gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                setIsModalOpen(false)
                setSelectedSubject(null)
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