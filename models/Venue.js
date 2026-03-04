const mongoose = require('mongoose');

const venueSchema = new mongoose.Schema({
  name: {
    type: String,
    required: [true, 'Venue name is required'],
    trim: true,
    maxlength: [100, 'Name cannot exceed 100 characters']
  },
  description: {
    type: String,
    required: [true, 'Description is required'],
    maxlength: [2000, 'Description cannot exceed 2000 characters']
  },
  owner: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  location: {
    address: {
      type: String,
      required: [true, 'Address is required']
    },
    city: {
      type: String,
      required: [true, 'City is required']
    },
    state: {
      type: String,
      required: [true, 'State is required']
    },
    zipCode: {
      type: String,
      required: [true, 'Zip code is required']
    },
    country: {
      type: String,
      default: 'USA'
    },
    coordinates: {
      latitude: Number,
      longitude: Number
    }
  },
  capacity: {
    type: Number,
    required: [true, 'Capacity is required'],
    min: [1, 'Capacity must be at least 1']
  },
  pricePerHour: {
    type: Number,
    required: [true, 'Price per hour is required'],
    min: [0, 'Price cannot be negative']
  },
  amenities: [{
    type: String,
    trim: true
  }],
  images: [{
    type: String
  }],
  venueType: {
    type: String,
    enum: ['conference', 'wedding', 'concert', 'corporate', 'party', 'other'],
    default: 'other'
  },
  availability: {
    type: Boolean,
    default: true
  },
  rating: {
    type: Number,
    default: 0,
    min: 0,
    max: 5
  },
  reviewCount: {
    type: Number,
    default: 0
  },
  isActive: {
    type: Boolean,
    default: true
  }
}, {
  timestamps: true
});

// Indexes for performance with high user load
venueSchema.index({ 'location.city': 1, 'location.state': 1 });
venueSchema.index({ venueType: 1 });
venueSchema.index({ pricePerHour: 1 });
venueSchema.index({ capacity: 1 });
venueSchema.index({ availability: 1, isActive: 1 });
venueSchema.index({ owner: 1 });

// Virtual for full address
venueSchema.virtual('fullAddress').get(function() {
  return `${this.location.address}, ${this.location.city}, ${this.location.state} ${this.location.zipCode}`;
});

module.exports = mongoose.model('Venue', venueSchema);
