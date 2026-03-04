const mongoose = require('mongoose');

const eventSchema = new mongoose.Schema({
  title: {
    type: String,
    required: [true, 'Event title is required'],
    trim: true,
    maxlength: [150, 'Title cannot exceed 150 characters']
  },
  description: {
    type: String,
    required: [true, 'Description is required'],
    maxlength: [3000, 'Description cannot exceed 3000 characters']
  },
  organizer: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  venue: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Venue',
    required: true
  },
  eventType: {
    type: String,
    enum: ['conference', 'wedding', 'concert', 'workshop', 'seminar', 'party', 'exhibition', 'other'],
    default: 'other'
  },
  startDate: {
    type: Date,
    required: [true, 'Start date is required']
  },
  endDate: {
    type: Date,
    required: [true, 'End date is required']
  },
  expectedAttendees: {
    type: Number,
    required: [true, 'Expected attendees is required'],
    min: [1, 'Must have at least 1 attendee']
  },
  status: {
    type: String,
    enum: ['pending', 'confirmed', 'cancelled', 'completed'],
    default: 'pending'
  },
  ticketPrice: {
    type: Number,
    default: 0,
    min: [0, 'Price cannot be negative']
  },
  totalCost: {
    type: Number,
    required: true
  },
  isPublic: {
    type: Boolean,
    default: true
  },
  images: [{
    type: String
  }],
  tags: [{
    type: String,
    trim: true
  }],
  requirements: {
    catering: {
      type: Boolean,
      default: false
    },
    av_equipment: {
      type: Boolean,
      default: false
    },
    parking: {
      type: Boolean,
      default: false
    },
    accessibility: {
      type: Boolean,
      default: false
    }
  }
}, {
  timestamps: true
});

// Indexes for query performance
eventSchema.index({ startDate: 1, endDate: 1 });
eventSchema.index({ venue: 1, startDate: 1 });
eventSchema.index({ organizer: 1 });
eventSchema.index({ status: 1 });
eventSchema.index({ eventType: 1 });
eventSchema.index({ isPublic: 1 });

// Validation: end date must be after start date
eventSchema.pre('save', function(next) {
  if (this.endDate <= this.startDate) {
    next(new Error('End date must be after start date'));
  }
  next();
});

module.exports = mongoose.model('Event', eventSchema);
