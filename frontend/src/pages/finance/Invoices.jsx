import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../../lib/api'
import Card from '../../components/ui/Card'
import Button from '../../components/ui/Button'
import Input from '../../components/ui/Input'
import Select from '../../components/ui/Select'
import Modal from '../../components/ui/Modal'
import LoadingSpinner from '../../components/ui/LoadingSpinner'

export default function Invoices() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedInvoice, setSelectedInvoice] = useState(null)
  const [filters, setFilters] = useState({ search: '', status: '', start_date: '', end_date: '' })
  
  const queryClient = useQueryClient()

  // Fetch invoices
  const { data: invoicesData, isLoading } = useQuery({
    queryKey: ['invoices', filters],
    queryFn: () => api.get('/api/finance/invoices/', { params: filters }),
  })

  // Create/Update mutation
  const mutation = useMutation({
    mutationFn: (data) => {
      if (selectedInvoice) {
        return api.patch(`/api/finance/invoices/${selectedInvoice.id}/`, data)
      }
      return api.post('/api/finance/invoices/', data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['invoices'] })
      setIsModalOpen(false)
      setSelectedInvoice(null)
    },
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    const formData = new FormData(e.target)
    mutation.mutate(Object.fromEntries(formData))
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR'
    }).format(amount)
  }

  const getStatusColor = (status) => {
    const colors = {
      paid: 'bg-green-100 text-green-800',
      pending: 'bg-yellow-100 text-yellow-800',
      overdue: 'bg-red-100 text-red-800',
      cancelled: 'bg-gray-100 text-gray-800',
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const getStatusLabel = (status) => {
    const labels = {
      paid: 'Lunas',
      pending: 'Menunggu',
      overdue: 'Jatuh Tempo',
      cancelled: 'Dibatalkan',
    }
    return labels[status] || status
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Tagihan</h1>
          <p className="text-gray-500">Kelola tagihan siswa/santri</p>
        </div>
        <Button onClick={() => setIsModalOpen(true)}>
          + Buat Tagihan
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <div className="flex flex-wrap gap-4">
          <div className="flex-1 min-w-[200px]">
            <Input
              placeholder="Cari invoice..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
            />
          </div>
          <div className="w-[200px]">
            <Select
              options={[
                { value: '', label: 'Semua Status' },
                { value: 'pending', label: 'Menunggu' },
                { value: 'paid', label: 'Lunas' },
                { value: 'overdue', label: 'Jatuh Tempo' },
              ]}
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
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
                  <th className="text-left py-3 px-4">No. Invoice</th>
                  <th className="text-left py-3 px-4">Siswa</th>
                  <th className="text-left py-3 px-4">Jenis Pembayaran</th>
                  <th className="text-left py-3 px-4">Jumlah</th>
                  <th className="text-left py-3 px-4">Jatuh Tempo</th>
                  <th className="text-left py-3 px-4">Status</th>
                  <th className="text-left py-3 px-4">Aksi</th>
                </tr>
              </thead>
              <tbody>
                {invoicesData?.results?.map((invoice) => (
                  <tr key={invoice.id} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4 font-medium">{invoice.invoice_number}</td>
                    <td className="py-3 px-4">{invoice.student?.name}</td>
                    <td className="py-3 px-4">{invoice.payment_type}</td>
                    <td className="py-3 px-4">{formatCurrency(invoice.amount)}</td>
                    <td className="py-3 px-4">{invoice.due_date}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-1 rounded text-sm ${getStatusColor(invoice.status)}`}>
                        {getStatusLabel(invoice.status)}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <Button 
                        variant="secondary"
                        size="sm"
                        onClick={() => {
                          setSelectedInvoice(invoice)
                          setIsModalOpen(true)
                        }}
                      >
                        Detail
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
          setSelectedInvoice(null)
        }}
        title={selectedInvoice ? 'Detail Tagihan' : 'Buat Tagihan'}
      >
        {selectedInvoice ? (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">No. Invoice</p>
                <p className="font-medium">{selectedInvoice.invoice_number}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Siswa</p>
                <p className="font-medium">{selectedInvoice.student?.name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Jenis Pembayaran</p>
                <p className="font-medium">{selectedInvoice.payment_type}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Jumlah</p>
                <p className="font-medium">{formatCurrency(selectedInvoice.amount)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Jatuh Tempo</p>
                <p className="font-medium">{selectedInvoice.due_date}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Status</p>
                <span className={`px-2 py-1 rounded text-sm ${getStatusColor(selectedInvoice.status)}`}>
                  {getStatusLabel(selectedInvoice.status)}
                </span>
              </div>
            </div>
            <div className="flex justify-end gap-2 mt-4">
              <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
                Tutup
              </Button>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              name="student"
              label="Siswa"
              placeholder="Nama siswa"
              required
            />
            <Input
              name="payment_type"
              label="Jenis Pembayaran"
              placeholder="contoh: SPP, DSP, Buku"
              required
            />
            <Input
              name="amount"
              label="Jumlah"
              type="number"
              placeholder="Masukkan jumlah"
              required
            />
            <Input
              name="due_date"
              label="Jatuh Tempo"
              type="date"
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
        )}
      </Modal>
    </div>
  )
}
