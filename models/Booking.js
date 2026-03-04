const mongoose = require('mongoose');

const bookingSchema = new mongoose.Schema({
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  venue: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Venue',
    required: true
  },
  event: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Event'
  },
  startDate: {
    type: Date,
    required: [true, 'Start date is required']
  },
  endDate: {
    type: Date,
    required: [true, 'End date is required']
  },
  duration: {
    type: Number, // in hours
    required: true
  },
  totalAmount: {
    type: Number,
    required: [true, 'Total amount is required'],
    min: [0, 'Amount cannot be negative']
  },
  status: {
    type: String,
    enum: ['pending', 'confirmed', 'cancelled', 'completed', 'refunded'],
    default: 'pending'
  },
  paymentStatus: {
    type: String,
    enum: ['pending', 'paid', 'failed', 'refunded'],
    default: 'pending'
  },
  paymentMethod: {
    type: String,
    enum: ['credit_card', 'debit_card', 'paypal', 'bank_transfer', 'cash'],
    default: 'credit_card'
  },
  transactionId: {
    type: String
  },
  guests: {
    type: Number,
    default: 1
  },
  specialRequests: {
    type: String,
    maxlength: [1000, 'Special requests cannot exceed 1000 characters']
  },
  cancellationReason: {
    type: String
  },
  refundAmount: {
    type: Number,
    default: 0
  }
}, {
  timestamps: true
});

// Indexes for scalability
bookingSchema.index({ user: 1, createdAt: -1 });
bookingSchema.index({ venue: 1, startDate: 1, endDate: 1 });
bookingSchema.index({ status: 1 });
bookingSchema.index({ paymentStatus: 1 });
bookingSchema.index({ startDate: 1, endDate: 1 });

// Prevent double bookings - check for overlapping dates
bookingSchema.index({ venue: 1, startDate: 1, endDate: 1 }, { 
  unique: true,
  partialFilterExpression: { status: { $in: ['pending', 'confirmed'] } }
});

// Calculate duration before saving
bookingSchema.pre('save', function(next) {
  if (this.isModified('startDate') || this.isModified('endDate')) {
    const diffMs = this.endDate - this.startDate;
    this.duration = Math.ceil(diffMs / (1000 * 60 * 60)); // Convert to hours
  }
  next();
});

module.exports = mongoose.model('Booking', bookingSchema);
