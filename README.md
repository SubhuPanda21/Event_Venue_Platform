# 🎪 Event Venue Platform - E-commerce Booking System

A scalable, production-ready event venue booking platform built with Node.js and MongoDB, designed to support **1,000+ daily users** with high performance and reliability.

## 🚀 Features

### Core Functionality
- **User Management**: Multi-role authentication (User, Venue Owner, Admin)
- **Venue Management**: Create, update, and manage event venues
- **Event Planning**: Comprehensive event creation and management
- **Booking System**: Real-time availability checking and booking management
- **Payment Integration**: Multiple payment methods with transaction tracking

### Performance & Scalability
- **Connection Pooling**: Optimized MongoDB connections (10 max, 5 min)
- **Rate Limiting**: Protects API from abuse (100 requests per 15 min per IP)
- **Caching Ready**: Structure supports Redis integration
- **Database Indexing**: Strategic indexes for high-performance queries
- **Compression**: Response compression for faster data transfer

### Security
- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt with salt rounds
- **Helmet.js**: Security headers protection
- **CORS Configuration**: Configurable cross-origin resource sharing
- **Input Validation**: express-validator for request validation
- **Role-Based Access Control**: Fine-grained permissions

### Monitoring & Logging
- **Winston Logger**: Comprehensive logging system
- **Morgan**: HTTP request logging
- **Health Check Endpoint**: System status monitoring
- **Error Tracking**: Centralized error handling

## 📋 Prerequisites

- Node.js >= 18.0.0
- MongoDB >= 5.0
- npm >= 9.0.0

## 🛠️ Installation

1. **Clone or extract the project**
   ```bash
   cd ecommerce-event-platform
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your configuration:
   ```env
   PORT=5000
   MONGODB_URI=mongodb://localhost:27017/event-platform
   JWT_SECRET=your-very-secure-secret-key-change-this
   ALLOWED_ORIGINS=http://localhost:3000
   ```

4. **Start MongoDB**
   ```bash
   # Using MongoDB service
   sudo systemctl start mongod
   
   # Or using Docker
   docker run -d -p 27017:27017 --name mongodb mongo:latest
   ```

5. **Seed the database (optional)**
   ```bash
   npm run seed
   ```
   This creates sample users, venues, events, and bookings for testing.

6. **Start the server**
   ```bash
   # Development mode with auto-reload
   npm run dev
   
   # Production mode
   npm start
   ```

The server will start on `http://localhost:5000`

## 📚 API Documentation

### Base URL
```
http://localhost:5000/api
```

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "name": "John Doe",
  "role": "user",
  "phone": "+1-555-1234"
}

Response: { token, user }
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

Response: { token, user }
```

#### Get Current User
```http
GET /api/auth/me
Authorization: Bearer <token>

Response: { user }
```

### Venue Endpoints

#### Get All Venues
```http
GET /api/venues?page=1&limit=10&city=New York&venueType=conference

Response: { venues[], pagination }
```

#### Get Venue by ID
```http
GET /api/venues/:id

Response: { venue }
```

#### Create Venue (Venue Owner/Admin only)
```http
POST /api/venues
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Grand Convention Center",
  "description": "Large event space...",
  "location": {
    "address": "123 Main St",
    "city": "New York",
    "state": "NY",
    "zipCode": "10001"
  },
  "capacity": 500,
  "pricePerHour": 500,
  "amenities": ["WiFi", "Parking", "AV Equipment"],
  "venueType": "conference"
}

Response: { message, venue }
```

#### Update Venue
```http
PUT /api/venues/:id
Authorization: Bearer <token>
Content-Type: application/json

{ ...updated fields... }

Response: { message, venue }
```

#### Get My Venues
```http
GET /api/venues/owner/my-venues
Authorization: Bearer <token>

Response: { venues[], count }
```

### Event Endpoints

#### Get All Events
```http
GET /api/events?page=1&limit=10&eventType=conference&status=confirmed

Response: { events[], pagination }
```

#### Get Event by ID
```http
GET /api/events/:id

Response: { event }
```

#### Create Event
```http
POST /api/events
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Tech Conference 2026",
  "description": "Annual tech event...",
  "venue": "venue_id_here",
  "eventType": "conference",
  "startDate": "2026-06-15T09:00:00Z",
  "endDate": "2026-06-15T17:00:00Z",
  "expectedAttendees": 300,
  "ticketPrice": 299,
  "isPublic": true
}

Response: { message, event }
```

#### Get My Events
```http
GET /api/events/my/organized
Authorization: Bearer <token>

Response: { events[], count }
```

### Booking Endpoints

#### Get All Bookings
```http
GET /api/bookings?page=1&limit=10&status=confirmed
Authorization: Bearer <token>

Response: { bookings[], pagination }
```

#### Create Booking
```http
POST /api/bookings
Authorization: Bearer <token>
Content-Type: application/json

{
  "venue": "venue_id_here",
  "startDate": "2026-07-20T14:00:00Z",
  "endDate": "2026-07-20T18:00:00Z",
  "guests": 50,
  "event": "event_id_here",
  "specialRequests": "Need vegan catering"
}

Response: { message, booking }
```

#### Confirm Booking (Venue Owner/Admin)
```http
PUT /api/bookings/:id/confirm
Authorization: Bearer <token>

Response: { message, booking }
```

#### Cancel Booking
```http
PUT /api/bookings/:id/cancel
Authorization: Bearer <token>
Content-Type: application/json

{
  "cancellationReason": "Schedule conflict"
}

Response: { message, booking }
```

#### Get Venue Bookings (Venue Owner)
```http
GET /api/bookings/venue/:venueId
Authorization: Bearer <token>

Response: { bookings[], count }
```

### User Endpoints (Admin)

#### Get All Users
```http
GET /api/users?page=1&limit=20&role=user
Authorization: Bearer <admin_token>

Response: { users[], pagination }
```

#### Get User Stats
```http
GET /api/users/stats/overview
Authorization: Bearer <admin_token>

Response: { stats: { total, active, verified, byRole } }
```

## 🗄️ Database Schema

### User
- email, password (hashed), name, role, phone, avatar
- isVerified, isActive, lastLogin
- Indexes: email, role

### Venue
- name, description, owner (ref: User)
- location (address, city, state, zipCode, coordinates)
- capacity, pricePerHour, amenities, venueType
- availability, rating, reviewCount
- Indexes: location, venueType, capacity, availability

### Event
- title, description, organizer (ref: User), venue (ref: Venue)
- eventType, startDate, endDate, expectedAttendees
- status, ticketPrice, totalCost, isPublic
- Indexes: dates, venue, organizer, status, eventType

### Booking
- user (ref: User), venue (ref: Venue), event (ref: Event)
- startDate, endDate, duration, totalAmount
- status, paymentStatus, paymentMethod, transactionId
- guests, specialRequests
- Indexes: user, venue+dates, status, paymentStatus

## 🧪 Testing

### Test Users (after seeding)
```
Admin: admin@eventplatform.com / admin123
Venue Owner: john@venues.com / password123
Event Organizer: jane@events.com / password123
Customer: mike@customer.com / password123
```

### Test with cURL
```bash
# Register
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123","name":"Test User"}'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@eventplatform.com","password":"admin123"}'

# Get venues
curl http://localhost:5000/api/venues

# Health check
curl http://localhost:5000/health
```

## 📊 Performance Optimization

### For 1,000+ Daily Users

1. **Database Optimization**
   - Strategic indexes on frequently queried fields
   - Connection pooling (10 max, 5 min connections)
   - Compound indexes for complex queries

2. **API Rate Limiting**
   - 100 requests per 15 minutes per IP
   - Protects against DDoS and abuse

3. **Response Optimization**
   - Gzip compression enabled
   - Pagination on all list endpoints
   - Selective field population

4. **Scalability Ready**
   - Stateless JWT authentication (horizontal scaling ready)
   - Can add Redis for session management
   - MongoDB replica sets for high availability

## 🔐 Security Best Practices

1. **Change default JWT_SECRET** in production
2. **Use HTTPS** in production
3. **Configure ALLOWED_ORIGINS** properly
4. **Enable MongoDB authentication**
5. **Regular security audits**: `npm audit`
6. **Keep dependencies updated**: `npm update`

## 🚀 Deployment

### Production Checklist
- [ ] Set NODE_ENV=production
- [ ] Configure production MongoDB URI
- [ ] Set strong JWT_SECRET
- [ ] Configure CORS allowed origins
- [ ] Set up reverse proxy (Nginx/Apache)
- [ ] Enable SSL/TLS certificates
- [ ] Set up monitoring (PM2, New Relic)
- [ ] Configure log rotation
- [ ] Set up database backups

### Deploy with PM2
```bash
npm install -g pm2
pm2 start server.js --name event-platform
pm2 startup
pm2 save
```

## 📁 Project Structure

```
ecommerce-event-platform/
├── models/           # Mongoose schemas
│   ├── User.js
│   ├── Venue.js
│   ├── Event.js
│   └── Booking.js
├── routes/           # API routes
│   ├── auth.js
│   ├── venues.js
│   ├── events.js
│   ├── bookings.js
│   └── users.js
├── middleware/       # Custom middleware
│   └── auth.js
├── utils/            # Utility functions
│   └── logger.js
├── scripts/          # Database scripts
│   └── seedData.js
├── logs/             # Application logs
├── server.js         # Entry point
├── package.json
└── .env.example
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

MIT License - feel free to use this project for learning or commercial purposes.

## 🆘 Support

For issues and questions:
- Check the API documentation above
- Review the code comments
- Check MongoDB connection
- Verify environment variables

## 🎯 Future Enhancements

- [ ] Payment gateway integration (Stripe/PayPal)
- [ ] Email notifications (SendGrid)
- [ ] Image upload (AWS S3/Cloudinary)
- [ ] Search with Elasticsearch
- [ ] Real-time chat (Socket.io)
- [ ] Calendar integration
- [ ] Review and rating system
- [ ] Analytics dashboard
- [ ] Mobile app API
- [ ] Multi-language support

---

**Built with ❤️ for high-performance event management**
