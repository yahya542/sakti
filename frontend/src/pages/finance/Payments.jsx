import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../../lib/api'
import Card from '../../components/ui/Card'
import Button from '../../components/ui/Button'
import Input from '../../components/ui/Input'
import Select from '../../components/ui/Select'
import Modal from '../../components/ui/Modal'
import LoadingSpinner from '../../components/ui/LoadingSpinner'

export default function Payments() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedPayment, setSelectedPayment] = useState(null)
  const [filters, setFilters] = useState({ search: '', start_date: '', end_date: '' })
  
  const queryClient = useQueryClient()

  // Fetch payments
  const { data: paymentsData, isLoading } = useQuery({
    queryKey: ['payments', filters],
    queryFn: () => api.get('/finance/payments/', { params: filters }),
  })

  // Create/Update mutation
  const mutation = useMutation({
    mutationFn: (data) => {
      if (selectedPayment) {
        return api.patch(`/finance/payments/${selectedPayment.id}/`, data)
      }
      return api.post('/finance/payments/', data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payments'] })
      setIsModalOpen(false)
      setSelectedPayment(null)
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

  const getMethodColor = (method) => {
    const colors = {
      cash: 'bg-blue-100 text-blue-800',
      transfer: 'bg-green-100 text-green-800',
      card: 'bg-purple-100 text-purple-800',
    }
    return colors[method] || 'bg-gray-100 text-gray-800'
  }

  const getMethodLabel = (method) => {
    const labels = {
      cash: 'Tunai',
      transfer: 'Transfer',
      card: 'Kartu',
    }
    return labels[method] || method
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Pembayaran</h1>
          <p className="text-gray-500">Kelola data pembayaran siswa/santri</p>
        </div>
        <Button onClick={() => setIsModalOpen(true)}>
          + Tambah Pembayaran
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <div className="flex flex-wrap gap-4">
          <div className="flex-1 min-w-[200px]">
            <Input
              placeholder="Cari pembayaran..."
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

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <div className="text-center">
            <p className="text-sm text-gray-500">Total Pembayaran</p>
            <p className="text-2xl font-bold text-gray-900">
              {formatCurrency(paymentsData?.summary?.total || 0)}
            </p>
          </div>
        </Card>
        <Card>
          <div className="text-center">
            <p className="text-sm text-gray-500">Jumlah Transaksi</p>
            <p className="text-2xl font-bold text-gray-900">
              {paymentsData?.summary?.count || 0}
            </p>
          </div>
        </Card>
        <Card>
          <div className="text-center">
            <p className="text-sm text-gray-500">Rata-rata Pembayaran</p>
            <p className="text-2xl font-bold text-gray-900">
              {formatCurrency(paymentsData?.summary?.average || 0)}
            </p>
          </div>
        </Card>
      </div>

      {/* Table */}
      <Card>
        {isLoading ? (
          <LoadingSpinner />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4">No. Pembayaran</th>
                  <th className="text-left py-3 px-4">Invoice</th>
                  <th className="text-left py-3 px-4">Siswa</th>
                  <th className="text-left py-3 px-4">Jumlah</th>
                  <th className="text-left py-3 px-4">Metode</th>
                  <th className="text-left py-3 px-4">Tanggal</th>
                  <th className="text-left py-3 px-4">Aksi</th>
                </tr>
              </thead>
              <tbody>
                {paymentsData?.results?.map((payment) => (
                  <tr key={payment.id} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4 font-medium">{payment.payment_number}</td>
                    <td className="py-3 px-4">{payment.invoice?.invoice_number}</td>
                    <td className="py-3 px-4">{payment.student?.name}</td>
                    <td className="py-3 px-4">{formatCurrency(payment.amount)}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-1 rounded text-sm ${getMethodColor(payment.method)}`}>
                        {getMethodLabel(payment.method)}
                      </span>
                    </td>
                    <td className="py-3 px-4">{payment.payment_date}</td>
                    <td className="py-3 px-4">
                      <Button 
                        variant="secondary"
                        size="sm"
                        onClick={() => {
                          setSelectedPayment(payment)
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
          setSelectedPayment(null)
        }}
        title={selectedPayment ? 'Detail Pembayaran' : 'Tambah Pembayaran'}
      >
        {selectedPayment ? (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">No. Pembayaran</p>
                <p className="font-medium">{selectedPayment.payment_number}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Invoice</p>
                <p className="font-medium">{selectedPayment.invoice?.invoice_number}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Siswa</p>
                <p className="font-medium">{selectedPayment.student?.name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Jumlah</p>
                <p className="font-medium">{formatCurrency(selectedPayment.amount)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Metode</p>
                <span className={`px-2 py-1 rounded text-sm ${getMethodColor(selectedPayment.method)}`}>
                  {getMethodLabel(selectedPayment.method)}
                </span>
              </div>
              <div>
                <p className="text-sm text-gray-500">Tanggal Pembayaran</p>
                <p className="font-medium">{selectedPayment.payment_date}</p>
              </div>
              {selectedPayment.notes && (
                <div className="col-span-2">
                  <p className="text-sm text-gray-500">Catatan</p>
                  <p className="font-medium">{selectedPayment.notes}</p>
                </div>
              )}
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
              name="invoice"
              label="Invoice"
              placeholder="No. Invoice"
              required
            />
            <Input
              name="student"
              label="Siswa"
              placeholder="Nama siswa"
              required
            />
            <Input
              name="amount"
              label="Jumlah"
              type="number"
              placeholder="Masukkan jumlah"
              required
            />
            <Select
              name="method"
              label="Metode Pembayaran"
              options={[
                { value: 'cash', label: 'Tunai' },
                { value: 'transfer', label: 'Transfer' },
                { value: 'card', label: 'Kartu' },
              ]}
              required
            />
            <Input
              name="payment_date"
              label="Tanggal Pembayaran"
              type="date"
              required
            />
            <Input
              name="notes"
              label="Catatan"
              placeholder="Catatan pembayaran"
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
