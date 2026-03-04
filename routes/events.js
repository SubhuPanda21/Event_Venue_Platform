const express = require('express');
const router = express.Router();
const { body, validationResult } = require('express-validator');
const Event = require('../models/Event');
const Venue = require('../models/Venue');
const { auth } = require('../middleware/auth');

// @route   GET /api/events
// @desc    Get all events with filtering
// @access  Public
router.get('/', async (req, res) => {
  try {
    const { 
      page = 1, 
      limit = 10, 
      eventType, 
      status,
      startDate,
      endDate,
      isPublic = true
    } = req.query;

    const filter = {};
    if (eventType) filter.eventType = eventType;
    if (status) filter.status = status;
    if (isPublic === 'true') filter.isPublic = true;
    if (startDate) filter.startDate = { $gte: new Date(startDate) };
    if (endDate) filter.endDate = { $lte: new Date(endDate) };

    const events = await Event.find(filter)
      .populate('organizer', 'name email')
      .populate('venue', 'name location pricePerHour')
      .sort({ startDate: 1 })
      .limit(parseInt(limit))
      .skip((parseInt(page) - 1) * parseInt(limit));

    const total = await Event.countDocuments(filter);

    res.json({
      events,
      pagination: {
        current: parseInt(page),
        pages: Math.ceil(total / parseInt(limit)),
        total
      }
    });
  } catch (error) {
    console.error('Get events error:', error);
    res.status(500).json({ error: 'Error fetching events' });
  }
});

// @route   GET /api/events/:id
// @desc    Get single event
// @access  Public
router.get('/:id', async (req, res) => {
  try {
    const event = await Event.findById(req.params.id)
      .populate('organizer', 'name email phone')
      .populate('venue');

    if (!event) {
      return res.status(404).json({ error: 'Event not found' });
    }

    res.json({ event });
  } catch (error) {
    console.error('Get event error:', error);
    res.status(500).json({ error: 'Error fetching event' });
  }
});

// @route   POST /api/events
// @desc    Create new event
// @access  Private
router.post('/', [
  auth,
  body('title').trim().notEmpty(),
  body('description').trim().notEmpty(),
  body('venue').isMongoId(),
  body('startDate').isISO8601(),
  body('endDate').isISO8601(),
  body('expectedAttendees').isInt({ min: 1 })
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { venue, startDate, endDate, expectedAttendees } = req.body;

    // Check if venue exists and is available
    const venueDoc = await Venue.findById(venue);
    if (!venueDoc) {
      return res.status(404).json({ error: 'Venue not found' });
    }

    if (!venueDoc.availability) {
      return res.status(400).json({ error: 'Venue is not available' });
    }

    // Check capacity
    if (expectedAttendees > venueDoc.capacity) {
      return res.status(400).json({ 
        error: `Expected attendees (${expectedAttendees}) exceeds venue capacity (${venueDoc.capacity})` 
      });
    }

    // Calculate total cost
    const start = new Date(startDate);
    const end = new Date(endDate);
    const durationHours = Math.ceil((end - start) / (1000 * 60 * 60));
    const totalCost = durationHours * venueDoc.pricePerHour;

    const event = new Event({
      ...req.body,
      organizer: req.userId,
      totalCost
    });

    await event.save();

    const populatedEvent = await Event.findById(event._id)
      .populate('organizer', 'name email')
      .populate('venue');

    res.status(201).json({
      message: 'Event created successfully',
      event: populatedEvent
    });
  } catch (error) {
    console.error('Create event error:', error);
    res.status(500).json({ error: 'Error creating event' });
  }
});

// @route   PUT /api/events/:id
// @desc    Update event
// @access  Private (organizer only)
router.put('/:id', auth, async (req, res) => {
  try {
    const event = await Event.findById(req.params.id);

    if (!event) {
      return res.status(404).json({ error: 'Event not found' });
    }

    // Check if user is organizer
    if (event.organizer.toString() !== req.userId.toString()) {
      return res.status(403).json({ error: 'Not authorized to update this event' });
    }

    const updatedEvent = await Event.findByIdAndUpdate(
      req.params.id,
      req.body,
      { new: true, runValidators: true }
    ).populate('organizer venue');

    res.json({
      message: 'Event updated successfully',
      event: updatedEvent
    });
  } catch (error) {
    console.error('Update event error:', error);
    res.status(500).json({ error: 'Error updating event' });
  }
});

// @route   DELETE /api/events/:id
// @desc    Cancel event
// @access  Private (organizer only)
router.delete('/:id', auth, async (req, res) => {
  try {
    const event = await Event.findById(req.params.id);

    if (!event) {
      return res.status(404).json({ error: 'Event not found' });
    }

    if (event.organizer.toString() !== req.userId.toString()) {
      return res.status(403).json({ error: 'Not authorized to cancel this event' });
    }

    event.status = 'cancelled';
    await event.save();

    res.json({ message: 'Event cancelled successfully' });
  } catch (error) {
    console.error('Cancel event error:', error);
    res.status(500).json({ error: 'Error cancelling event' });
  }
});

// @route   GET /api/events/my/organized
// @desc    Get events organized by current user
// @access  Private
router.get('/my/organized', auth, async (req, res) => {
  try {
    const events = await Event.find({ organizer: req.userId })
      .populate('venue')
      .sort({ startDate: 1 });

    res.json({ events, count: events.length });
  } catch (error) {
    console.error('Get my events error:', error);
    res.status(500).json({ error: 'Error fetching your events' });
  }
});

module.exports = router;
