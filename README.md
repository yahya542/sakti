# SAKTI - Sistem Akademik Terpadu Indonesia

## Panduan Setup Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis
- RabbitMQ (optional untuk Celery)

### Backend Setup

```bash
# Clone repository
git clone https://github.com/sajakcodingan/sakti.git
cd sakti

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env dengan konfigurasi database dan secrets

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Environment Variables (.env)

```env
# Database
DB_NAME=sakti_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# JWT
JWT_SECRET_KEY=your-secret-key-here
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440

# Application
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Payment Gateway (optional)
MIDTRANS_SERVER_KEY=your-key
MIDTRANS_CLIENT_KEY=your-key
```

### Docker Setup (Production)

```bash
docker-compose up -d
```

## Struktur Project

```
sakti/
├── backend/              # Django Project
│   ├── sakti/           # Main project config
│   ├── apps/            # Django Applications
│   │   ├── tenants/    # Multi-tenancy
│   │   ├── accounts/   # User management
│   │   ├── rbac/       # Role-based access
│   │   ├── academic/   # Academic data
│   │   ├── smart_linking/ # Auto family linking
│   │   ├── activities/ # Attendance & scores
│   │   └── finance/    # Payments & invoicing
│   └── requirements.txt
├── frontend/            # React + Vite
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── stores/
│   └── package.json
└── docker-compose.yml
```

## API Endpoints

### Authentication
- `POST /api/auth/login/` - Login
- `POST /api/auth/logout/` - Logout
- `POST /api/auth/refresh/` - Refresh token
- `GET /api/auth/me/` - Current user

### Tenants
- `GET /api/tenants/` - List tenants (super admin)
- `POST /api/tenants/` - Create tenant
- `GET /api/tenants/{slug}/` - Get tenant config

### Academic
- `GET /api/students/` - List students
- `POST /api/students/` - Create student
- `GET /api/teachers/` - List teachers
- `GET /api/classes/` - List classes
- `GET /api/subjects/` - List subjects

### Activities
- `POST /api/attendance/` - Create attendance
- `GET /api/attendance/student/{id}/` - Student attendance
- `POST /api/scores/` - Create score
- `GET /api/scores/student/{id}/` - Student scores
- `GET /api/timeline/` - Parent timeline feed

### Finance
- `POST /api/invoices/` - Create invoice
- `GET /api/invoices/student/{id}/` - Student invoices
- `POST /api/payments/ callback/` - Payment callback

## Demo Credentials

```
Super Admin: admin@sakti.id / admin123
Admin School: admin@uim.sakti.id / admin123
Teacher: guru@uim.sakti.id / guru123
Student: siswa@uim.sakti.id / siswa123
Parent: wali@uim.sakti.id / wali123
```

## License

Copyright © 2026 Sajakcodingan.
