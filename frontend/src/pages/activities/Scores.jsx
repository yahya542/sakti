import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../../lib/api'
import Card from '../../components/ui/Card'
import Button from '../../components/ui/Button'
import Input from '../../components/ui/Input'
import Select from '../../components/ui/Select'
import Modal from '../../components/ui/Modal'
import LoadingSpinner from '../../components/ui/LoadingSpinner'

export default function Scores() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedScore, setSelectedScore] = useState(null)
  const [filters, setFilters] = useState({ search: '', class_id: '', subject_id: '' })
  
  const queryClient = useQueryClient()

  // Fetch scores
  const { data: scoresData, isLoading } = useQuery({
    queryKey: ['scores', filters],
    queryFn: () => api.get('/api/activities/scores/', { params: filters }),
  })

  // Fetch classes for filter
  const { data: classes } = useQuery({
    queryKey: ['classes'],
    queryFn: () => api.get('/api/academic/classes/'),
  })

  // Fetch subjects for filter
  const { data: subjects } = useQuery({
    queryKey: ['subjects'],
    queryFn: () => api.get('/api/academic/subjects/'),
  })

  // Create/Update mutation
  const mutation = useMutation({
    mutationFn: (data) => {
      if (selectedScore) {
        return api.patch(`/api/activities/scores/${selectedScore.id}/`, data)
      }
      return api.post('/api/activities/scores/', data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scores'] })
      setIsModalOpen(false)
      setSelectedScore(null)
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

  const subjectOptions = subjects?.results?.map(s => ({
    value: s.id,
    label: s.name,
  })) || []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Nilai</h1>
          <p className="text-gray-500">Kelola nilai siswa/santri</p>
        </div>
        <Button onClick={() => setIsModalOpen(true)}>
          + Tambah Nilai
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
            <Select
              options={subjectOptions}
              value={filters.subject_id}
              onChange={(e) => setFilters({ ...filters, subject_id: e.target.value })}
              placeholder="Pilih Mata Pelajaran"
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
                  <th className="text-left py-3 px-4">Siswa</th>
                  <th className="text-left py-3 px-4">Kelas</th>
                  <th className="text-left py-3 px-4">Mata Pelajaran</th>
                  <th className="text-left py-3 px-4">Jenis Nilai</th>
                  <th className="text-left py-3 px-4">Nilai</th>
                  <th className="text-left py-3 px-4">Aksi</th>
                </tr>
              </thead>
              <tbody>
                {scoresData?.results?.map((score) => (
                  <tr key={score.id} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4">{score.student?.name}</td>
                    <td className="py-3 px-4">{score.student?.class?.name}</td>
                    <td className="py-3 px-4">{score.subject?.name}</td>
                    <td className="py-3 px-4">{score.score_type}</td>
                    <td className="py-3 px-4 font-semibold">{score.value}</td>
                    <td className="py-3 px-4">
                      <Button 
                        variant="secondary"
                        size="sm"
                        onClick={() => {
                          setSelectedScore(score)
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
          setSelectedScore(null)
        }}
        title={selectedScore ? 'Edit Nilai' : 'Tambah Nilai'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            name="student"
            label="Siswa"
            placeholder="Nama siswa"
            defaultValue={selectedScore?.student?.name}
            required
          />
          <Select
            name="subject"
            label="Mata Pelajaran"
            options={subjectOptions}
            defaultValue={selectedScore?.subject?.id}
            required
          />
          <Select
            name="score_type"
            label="Jenis Nilai"
            options={[
              { value: 'tugas', label: 'Tugas' },
              { value: 'uts', label: 'UTS' },
              { value: 'uas', label: 'UAS' },
              { value: 'praktek', label: 'Praktek' },
            ]}
            defaultValue={selectedScore?.score_type}
            required
          />
          <Input
            name="value"
            label="Nilai"
            type="number"
            min="0"
            max="100"
            placeholder="Masukkan nilai"
            defaultValue={selectedScore?.value}
            required
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
