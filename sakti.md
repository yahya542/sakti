# 🛡️ SAKTI: Sistem Akademik Terpadu Indonesia
> **The Ultimate School & Pesantren Operating System**  
> Platform SaaS (Software as a Service) yang mengintegrasikan administrasi, akademik, keuangan, dan komunikasi dalam satu ekosistem digital untuk Sekolah dan Pesantren di Indonesia.

---

## 🌟 Visi & Konsep Utama
SAKTI dirancang dengan arsitektur **Multi-Tenancy**, memungkinkan satu instalasi aplikasi melayani banyak instansi secara independen. Setiap instansi memiliki identitas eksklusif dengan skema:
**`SAKTI-[KODE_INSTANSI]`** (Contoh: *SAKTI-UIM*, *SAKTI-UNESA*, *SAKTI-ALFALAH*).

### Pilar Utama:
- **Transparansi**: Wali Murid/Santri mendapatkan update real-time.
- **Integritas**: Setiap perubahan data sensitif dicatat dalam *Audit Logs*.
- **Otomatisasi**: Relasi keluarga otomatis menggunakan No KK dan kalkulasi e-Rapor instan.

---

## 🛠️ Tech Stack & Arsitektur


| Component | Technology | Detail |
| :--- | :--- | :--- |
| **Backend** | **Django 5.x** | Kuat di ORM, Security, dan Admin Panel. |
| **API Layer** | **Django Rest Framework** | Arsitektur API-first untuk mobile/web. |
| **Frontend** | **React.js (Vite)** | Dashboard dinamis dengan Tanstack Query. |
| **Database** | **PostgreSQL** | Relasi data kompleks dan skema multi-tenant. |
| **Real-time** | **Redis & WebSockets** | Notifikasi instan & Timeline feed. |
| **Tasks** | **Celery & RabbitMQ** | Background jobs untuk laporan PDF & Billing. |
| **Styling** | **Tailwind CSS** | Desain modern, responsif, dan ringan. |

---

## 📂 Struktur Modul & Database (Backend)

Sistem dibagi menjadi **Django Apps** yang modular:

### 1. `tenants` (Pusat Kendali Instansi)
Mengelola konfigurasi khusus tiap sekolah/pesantren.
- **Fields**: `name`, `sub_brand_slug`, `logo`, `primary_color`, `theme_config`, `is_active`.

### 2. `accounts` & `rbac` (Security)
Manajemen akses berdasarkan peran (Role Based Access Control).
- **Roles**: Super Admin, Admin Sekolah, Guru/Ustadz, Siswa/Santri, Wali Murid/Santri.

### 3. `academic` (Data Induk)
- **Siswa/Santri**: Menyimpan Biografi, NIS/NISN, dan **Nomor KK**.
- **Guru/Ustadz**: Data Kepegawaian, NIP, Spesialisasi Mapel/Kitab.
- **Classes/Madrasah**: Relasi Siswa/Santri ke Kelas dan Wali Kelas/Ustadz Pendamping.

### 4. `smart_linking` (Logic Khusus)
Modul otomatisasi relasi keluarga.
- **Logic**: Saat akun Wali Murid/Santri dibuat, sistem melakukan *cross-check* field `no_kk` pada tabel Siswa/Santri. Jika cocok, relasi dibuat otomatis tanpa intervensi Admin.

### 5. `activities` (Monitoring)
- **Attendance**: Presensi harian, per jam pelajaran, atau kegiatan ekstrakurikuler/diniyah.
- **Scores**: Input nilai harian, UTS, UAS, dan tugas.
- **Timeline**: Mengirimkan sinyal (Signal) ke feed wali jika ada input nilai atau absen baru.

### 6. `finance` (Fintech Sekolah)
- **Invoicing**: Generate tagihan SPP bulanan otomatis.
- **Payments**: Integrasi API Payment Gateway (Midtrans/Xendit) untuk pembayaran VA/E-Wallet.

---

## ✨ Fitur Unggulan (Detailed)

### 📱 Social-Style Timeline
Wali Murid/Santri memiliki dashboard "Feed" yang menampilkan:
- Foto kegiatan Siswa/Santri di kelas/pondok.
- Pengumuman nilai ujian yang baru keluar.
- Riwayat kehadiran (Masuk/Terlambat/Izin).

### 🎨 Dynamic Branding (White-Label)
Saat login ke `uim.sakti.id`, seluruh UI React akan berubah:
- Logo berganti menjadi Logo UIM.
- Tema warna dashboard menyesuaikan identitas visual UIM.
- Nama aplikasi di Header menjadi **SAKTI-UIM**.

### 📄 E-Rapor Engine
Generate laporan hasil belajar ke PDF dengan standar nasional atau custom pesantren (Syahadah). Mendukung tanda tangan digital (QR Code).

### 🔒 Audit Logs & Security
Menjamin tidak ada "Nilai Siluman". Setiap perubahan data nilai oleh Guru/Ustadz akan dicatat:
- *Siapa, Kapan, Dari Nilai Berapa, Menjadi Nilai Berapa.*

---

## 🗺️ Roadmap Pengembangan (30 Hari)

### 📅 Minggu 1: Core Engine
- [ ] Setup Django Multi-tenancy & Database Schema.
- [ ] Implementasi JWT Authentication & RBAC.
- [ ] Setup Dashboard Base Layout (React + Tailwind).

### 📅 Minggu 2: Data & Smart Linking
- [ ] Modul Master Data (Siswa/Santri, Guru/Ustadz, Mapel/Kitab).
- [ ] Pengembangan Logic **Auto-Linking No KK**.
- [ ] Setup Media Storage untuk foto kegiatan.

### 📅 Minggu 3: Academic & Timeline
- [ ] Fitur Presensi (Mobile-friendly).
- [ ] Sistem Input Nilai & Kalkulasi Rapor.
- [ ] Implementasi Timeline Event System (Feed Wali).

### 📅 Minggu 4: Finance & Production
- [ ] Integrasi Payment Gateway (SPP Online).
- [ ] Fitur Export PDF Rapor & Invoices.
- [ ] Deployment ke Cloud (VPS + Docker + SSL).

---

## 🤝 Kontribusi & Lisensi
Proyek ini dikembangkan untuk memajukan kualitas administrasi pendidikan di Indonesia.  
**Hak Cipta © 2026 Sajakcodingan.**  
*Sinergi Pendidikan dalam Satu Genggaman.*
