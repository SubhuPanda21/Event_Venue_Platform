const express = require('express');
const router = express.Router();
const { body, validationResult } = require('express-validator');
const Booking = require('../models/Booking');
const Venue = require('../models/Venue');
const { auth } = require('../middleware/auth');

// @route   GET /api/bookings
// @desc    Get all bookings (admin) or user's bookings
// @access  Private
router.get('/', auth, async (req, res) => {
  try {
    const { page = 1, limit = 10, status } = req.query;
    
    // Admin can see all bookings, users see only their own
    const filter = req.user.role === 'admin' ? {} : { user: req.userId };
    if (status) filter.status = status;

    const bookings = await Booking.find(filter)
      .populate('user', 'name email')
      .populate('venue', 'name location pricePerHour')
      .populate('event', 'title eventType')
      .sort({ createdAt: -1 })
      .limit(parseInt(limit))
      .skip((parseInt(page) - 1) * parseInt(limit));

    const total = await Booking.countDocuments(filter);

    res.json({
      bookings,
      pagination: {
        current: parseInt(page),
        pages: Math.ceil(total / parseInt(limit)),
        total
      }
    });
  } catch (error) {
    console.error('Get bookings error:', error);
    res.status(500).json({ error: 'Error fetching bookings' });
  }
});

// @route   GET /api/bookings/:id
// @desc    Get single booking
// @access  Private
router.get('/:id', auth, async (req, res) => {
  try {
    const booking = await Booking.findById(req.params.id)
      .populate('user', 'name email phone')
      .populate('venue')
      .populate('event');

    if (!booking) {
      return res.status(404).json({ error: 'Booking not found' });
    }

    // Check if user has access to this booking
    if (booking.user._id.toString() !== req.userId.toString() && req.user.role !== 'admin') {
      return res.status(403).json({ error: 'Access denied' });
    }

    res.json({ booking });
  } catch (error) {
    console.error('Get booking error:', error);
    res.status(500).json({ error: 'Error fetching booking' });
  }
});

// @route   POST /api/bookings
// @desc    Create new booking
// @access  Private
router.post('/', [
  auth,
  body('venue').isMongoId(),
  body('startDate').isISO8601(),
  body('endDate').isISO8601(),
  body('guests').isInt({ min: 1 })
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { venue, startDate, endDate, guests, event, specialRequests } = req.body;

    // Check if venue exists
    const venueDoc = await Venue.findById(venue);
    if (!venueDoc) {
      return res.status(404).json({ error: 'Venue not found' });
    }

    if (!venueDoc.availability) {
      return res.status(400).json({ error: 'Venue is not available' });
    }

    // Check capacity
    if (guests > venueDoc.capacity) {
      return res.status(400).json({ 
        error: `Number of guests (${guests}) exceeds venue capacity (${venueDoc.capacity})` 
      });
    }

    const start = new Date(startDate);
    const end = new Date(endDate);

    // Check for overlapping bookings
    const overlapping = await Booking.findOne({
      venue,
      status: { $in: ['pending', 'confirmed'] },
      $or: [
        { startDate: { $lt: end }, endDate: { $gt: start } }
      ]
    });

    if (overlapping) {
      return res.status(400).json({ 
        error: 'Venue is already booked for the selected time slot' 
      });
    }

    // Calculate total amount
    const durationHours = Math.ceil((end - start) / (1000 * 60 * 60));
    const totalAmount = durationHours * venueDoc.pricePerHour;

    const booking = new Booking({
      user: req.userId,
      venue,
      event,
      startDate,
      endDate,
      duration: durationHours,
      totalAmount,
      guests,
      specialRequests
    });

    await booking.save();

    const populatedBooking = await Booking.findById(booking._id)
      .populate('user', 'name email')
      .populate('venue')
      .populate('event');

    res.status(201).json({
      message: 'Booking created successfully',
      booking: populatedBooking
    });
  } catch (error) {
    console.error('Create booking error:', error);
    if (error.code === 11000) {
      return res.status(400).json({ error: 'Venue is already booked for this time slot' });
    }
    res.status(500).json({ error: 'Error creating booking' });
  }
});

// @route   PUT /api/bookings/:id/confirm
// @desc    Confirm booking
// @access  Private (venue owner or admin)
router.put('/:id/confirm', auth, async (req, res) => {
  try {
    const booking = await Booking.findById(req.params.id).populate('venue');

    if (!booking) {
      return res.status(404).json({ error: 'Booking not found' });
    }

    // Check if user is venue owner or admin
    if (booking.venue.owner.toString() !== req.userId.toString() && req.user.role !== 'admin') {
      return res.status(403).json({ error: 'Not authorized to confirm this booking' });
    }

    booking.status = 'confirmed';
    await booking.save();

    res.json({
      message: 'Booking confirmed successfully',
      booking
    });
  } catch (error) {
    console.error('Confirm booking error:', error);
    res.status(500).json({ error: 'Error confirming booking' });
  }
});

// @route   PUT /api/bookings/:id/cancel
// @desc    Cancel booking
// @access  Private (user or admin)
router.put('/:id/cancel', auth, async (req, res) => {
  try {
    const booking = await Booking.findById(req.params.id);

    if (!booking) {
      return res.status(404).json({ error: 'Booking not found' });
    }

    // Check if user owns this booking or is admin
    if (booking.user.toString() !== req.userId.toString() && req.user.role !== 'admin') {
      return res.status(403).json({ error: 'Not authorized to cancel this booking' });
    }

    const { cancellationReason } = req.body;

    booking.status = 'cancelled';
    booking.cancellationReason = cancellationReason;
    
    // Calculate refund (example: 80% refund if cancelled 24h before)
    const hoursUntilStart = (new Date(booking.startDate) - new Date()) / (1000 * 60 * 60);
    if (hoursUntilStart > 24) {
      booking.refundAmount = booking.totalAmount * 0.8;
      booking.paymentStatus = 'refunded';
    }

    await booking.save();

    res.json({
      message: 'Booking cancelled successfully',
      booking
    });
  } catch (error) {
    console.error('Cancel booking error:', error);
    res.status(500).json({ error: 'Error cancelling booking' });
  }
});

// @route   PUT /api/bookings/:id/payment
// @desc    Update payment status
// @access  Private
router.put('/:id/payment', auth, async (req, res) => {
  try {
    const booking = await Booking.findById(req.params.id);

    if (!booking) {
      return res.status(404).json({ error: 'Booking not found' });
    }

    if (booking.user.toString() !== req.userId.toString()) {
      return res.status(403).json({ error: 'Access denied' });
    }

    const { paymentStatus, transactionId, paymentMethod } = req.body;

    booking.paymentStatus = paymentStatus;
    if (transactionId) booking.transactionId = transactionId;
    if (paymentMethod) booking.paymentMethod = paymentMethod;

    await booking.save();

    res.json({
      message: 'Payment status updated successfully',
      booking
    });
  } catch (error) {
    console.error('Update payment error:', error);
    res.status(500).json({ error: 'Error updating payment status' });
  }
});

// @route   GET /api/bookings/venue/:venueId
// @desc    Get bookings for a specific venue
// @access  Private (venue owner)
router.get('/venue/:venueId', auth, async (req, res) => {
  try {
    const venue = await Venue.findById(req.params.venueId);

    if (!venue) {
      return res.status(404).json({ error: 'Venue not found' });
    }

    // Check if user is venue owner or admin
    if (venue.owner.toString() !== req.userId.toString() && req.user.role !== 'admin') {
      return res.status(403).json({ error: 'Access denied' });
    }

    const bookings = await Booking.find({ venue: req.params.venueId })
      .populate('user', 'name email phone')
      .populate('event', 'title eventType')
      .sort({ startDate: 1 });

    res.json({ bookings, count: bookings.length });
  } catch (error) {
    console.error('Get venue bookings error:', error);
    res.status(500).json({ error: 'Error fetching venue bookings' });
  }
});

module.exports = router;
