const express = require('express');
const router = express.Router();
const { body, validationResult } = require('express-validator');
const Venue = require('../models/Venue');
const { auth, authorize } = require('../middleware/auth');

// @route   GET /api/venues
// @desc    Get all venues with filtering and pagination
// @access  Public
router.get('/', async (req, res) => {
  try {
    const { 
      page = 1, 
      limit = 10, 
      city, 
      state, 
      venueType, 
      minCapacity, 
      maxPrice,
      sortBy = 'createdAt',
      order = 'desc'
    } = req.query;

    // Build filter
    const filter = { isActive: true, availability: true };
    if (city) filter['location.city'] = new RegExp(city, 'i');
    if (state) filter['location.state'] = new RegExp(state, 'i');
    if (venueType) filter.venueType = venueType;
    if (minCapacity) filter.capacity = { $gte: parseInt(minCapacity) };
    if (maxPrice) filter.pricePerHour = { $lte: parseFloat(maxPrice) };

    // Build sort
    const sort = {};
    sort[sortBy] = order === 'asc' ? 1 : -1;

    // Execute query with pagination
    const venues = await Venue.find(filter)
      .populate('owner', 'name email')
      .sort(sort)
      .limit(parseInt(limit))
      .skip((parseInt(page) - 1) * parseInt(limit));

    const total = await Venue.countDocuments(filter);

    res.json({
      venues,
      pagination: {
        current: parseInt(page),
        pages: Math.ceil(total / parseInt(limit)),
        total,
        limit: parseInt(limit)
      }
    });
  } catch (error) {
    console.error('Get venues error:', error);
    res.status(500).json({ error: 'Error fetching venues' });
  }
});

// @route   GET /api/venues/:id
// @desc    Get single venue by ID
// @access  Public
router.get('/:id', async (req, res) => {
  try {
    const venue = await Venue.findById(req.params.id)
      .populate('owner', 'name email phone');

    if (!venue) {
      return res.status(404).json({ error: 'Venue not found' });
    }

    res.json({ venue });
  } catch (error) {
    console.error('Get venue error:', error);
    res.status(500).json({ error: 'Error fetching venue' });
  }
});

// @route   POST /api/venues
// @desc    Create a new venue
// @access  Private (venue_owner, admin)
router.post('/', [
  auth,
  authorize('venue_owner', 'admin'),
  body('name').trim().notEmpty(),
  body('description').trim().notEmpty(),
  body('capacity').isInt({ min: 1 }),
  body('pricePerHour').isFloat({ min: 0 })
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const venueData = {
      ...req.body,
      owner: req.userId
    };

    const venue = new Venue(venueData);
    await venue.save();

    res.status(201).json({
      message: 'Venue created successfully',
      venue
    });
  } catch (error) {
    console.error('Create venue error:', error);
    res.status(500).json({ error: 'Error creating venue' });
  }
});

// @route   PUT /api/venues/:id
// @desc    Update venue
// @access  Private (owner, admin)
router.put('/:id', [auth], async (req, res) => {
  try {
    const venue = await Venue.findById(req.params.id);

    if (!venue) {
      return res.status(404).json({ error: 'Venue not found' });
    }

    // Check if user is owner or admin
    if (venue.owner.toString() !== req.userId.toString() && req.user.role !== 'admin') {
      return res.status(403).json({ error: 'Not authorized to update this venue' });
    }

    const updatedVenue = await Venue.findByIdAndUpdate(
      req.params.id,
      req.body,
      { new: true, runValidators: true }
    );

    res.json({
      message: 'Venue updated successfully',
      venue: updatedVenue
    });
  } catch (error) {
    console.error('Update venue error:', error);
    res.status(500).json({ error: 'Error updating venue' });
  }
});

// @route   DELETE /api/venues/:id
// @desc    Delete venue (soft delete)
// @access  Private (owner, admin)
router.delete('/:id', auth, async (req, res) => {
  try {
    const venue = await Venue.findById(req.params.id);

    if (!venue) {
      return res.status(404).json({ error: 'Venue not found' });
    }

    // Check if user is owner or admin
    if (venue.owner.toString() !== req.userId.toString() && req.user.role !== 'admin') {
      return res.status(403).json({ error: 'Not authorized to delete this venue' });
    }

    // Soft delete
    venue.isActive = false;
    await venue.save();

    res.json({ message: 'Venue deleted successfully' });
  } catch (error) {
    console.error('Delete venue error:', error);
    res.status(500).json({ error: 'Error deleting venue' });
  }
});

// @route   GET /api/venues/owner/my-venues
// @desc    Get venues owned by current user
// @access  Private
router.get('/owner/my-venues', auth, async (req, res) => {
  try {
    const venues = await Venue.find({ owner: req.userId })
      .sort({ createdAt: -1 });

    res.json({ venues, count: venues.length });
  } catch (error) {
    console.error('Get my venues error:', error);
    res.status(500).json({ error: 'Error fetching your venues' });
  }
});

module.exports = router;
