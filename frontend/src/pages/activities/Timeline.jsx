import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '../../lib/api'
import Card from '../../components/ui/Card'
import Button from '../../components/ui/Button'
import Input from '../../components/ui/Input'

export default function Timeline() {
  const [filters, setFilters] = useState({ search: '', start_date: '', end_date: '' })

  // Fetch timeline events
  const { data: timelineData, isLoading } = useQuery({
    queryKey: ['timeline', filters],
    queryFn: () => api.get('/api/activities/timeline/', { params: filters }),
  })

  const formatDate = (dateStr) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('id-ID', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  const getEventTypeColor = (type) => {
    const colors = {
      assignment: 'bg-blue-100 border-blue-500',
      exam: 'bg-red-100 border-red-500',
      event: 'bg-green-100 border-green-500',
      announcement: 'bg-yellow-100 border-yellow-500',
    }
    return colors[type] || 'bg-gray-100 border-gray-500'
  }

  const getEventTypeLabel = (type) => {
    const labels = {
      assignment: 'Tugas',
      exam: 'Ujian',
      event: 'Acara',
      announcement: 'Pengumuman',
    }
    return labels[type] || type
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Timeline</h1>
          <p className="text-gray-500">Jadwal dan aktivitas kegiatan sekolah/pesantren</p>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <div className="flex flex-wrap gap-4">
          <div className="flex-1 min-w-[200px]">
            <Input
              placeholder="Cari kegiatan..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
            />
          </div>
          <div className="w-[200px]">
            <Input
              type="date"
              placeholder="Dari Tanggal"
              value={filters.start_date}
              onChange={(e) => setFilters({ ...filters, start_date: e.target.value })}
            />
          </div>
          <div className="w-[200px]">
            <Input
              type="date"
              placeholder="Sampai Tanggal"
              value={filters.end_date}
              onChange={(e) => setFilters({ ...filters, end_date: e.target.value })}
            />
          </div>
        </div>
      </Card>

      {/* Timeline */}
      <div className="space-y-4">
        {isLoading ? (
          <Card>
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          </Card>
        ) : timelineData?.results?.length === 0 ? (
          <Card>
            <div className="text-center py-12 text-gray-500">
              Tidak ada kegiatan
            </div>
          </Card>
        ) : (
          timelineData?.results?.map((event) => (
            <Card key={event.id} className={`border-l-4 ${getEventTypeColor(event.event_type)}`}>
              <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      event.event_type === 'assignment' ? 'bg-blue-100 text-blue-800' :
                      event.event_type === 'exam' ? 'bg-red-100 text-red-800' :
                      event.event_type === 'event' ? 'bg-green-100 text-green-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {getEventTypeLabel(event.event_type)}
                    </span>
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900">{event.title}</h3>
                  <p className="text-gray-600 mt-1">{event.description}</p>
                  {event.subject && (
                    <p className="text-sm text-gray-500 mt-2">
                      Mata Pelajaran: {event.subject.name}
                    </p>
                  )}
                  {event.class && (
                    <p className="text-sm text-gray-500">
                      Kelas: {event.class.name}
                    </p>
                  )}
                </div>
                <div className="text-right">
                  <p className="font-medium text-gray-900">{formatDate(event.date)}</p>
                  {event.start_time && (
                    <p className="text-sm text-gray-500">
                      {event.start_time} - {event.end_time || 'Selesai'}
                    </p>
                  )}
                </div>
              </div>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}