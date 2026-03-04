const express = require('express');
const router = express.Router();
const User = require('../models/User');
const { auth, authorize } = require('../middleware/auth');

// @route   GET /api/users
// @desc    Get all users
// @access  Private (admin only)
router.get('/', [auth, authorize('admin')], async (req, res) => {
  try {
    const { page = 1, limit = 20, role } = req.query;

    const filter = {};
    if (role) filter.role = role;

    const users = await User.find(filter)
      .select('-password')
      .sort({ createdAt: -1 })
      .limit(parseInt(limit))
      .skip((parseInt(page) - 1) * parseInt(limit));

    const total = await User.countDocuments(filter);

    res.json({
      users,
      pagination: {
        current: parseInt(page),
        pages: Math.ceil(total / parseInt(limit)),
        total
      }
    });
  } catch (error) {
    console.error('Get users error:', error);
    res.status(500).json({ error: 'Error fetching users' });
  }
});

// @route   GET /api/users/:id
// @desc    Get user by ID
// @access  Private (admin or self)
router.get('/:id', auth, async (req, res) => {
  try {
    // Users can only view their own profile unless they're admin
    if (req.params.id !== req.userId.toString() && req.user.role !== 'admin') {
      return res.status(403).json({ error: 'Access denied' });
    }

    const user = await User.findById(req.params.id).select('-password');

    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    res.json({ user });
  } catch (error) {
    console.error('Get user error:', error);
    res.status(500).json({ error: 'Error fetching user' });
  }
});

// @route   PUT /api/users/:id
// @desc    Update user
// @access  Private (admin or self)
router.put('/:id', auth, async (req, res) => {
  try {
    if (req.params.id !== req.userId.toString() && req.user.role !== 'admin') {
      return res.status(403).json({ error: 'Access denied' });
    }

    const { name, phone, avatar } = req.body;
    
    const updateData = {};
    if (name) updateData.name = name;
    if (phone) updateData.phone = phone;
    if (avatar) updateData.avatar = avatar;

    // Only admin can change role
    if (req.body.role && req.user.role === 'admin') {
      updateData.role = req.body.role;
    }

    const user = await User.findByIdAndUpdate(
      req.params.id,
      updateData,
      { new: true, runValidators: true }
    ).select('-password');

    res.json({
      message: 'User updated successfully',
      user
    });
  } catch (error) {
    console.error('Update user error:', error);
    res.status(500).json({ error: 'Error updating user' });
  }
});

// @route   DELETE /api/users/:id
// @desc    Deactivate user
// @access  Private (admin only)
router.delete('/:id', [auth, authorize('admin')], async (req, res) => {
  try {
    const user = await User.findByIdAndUpdate(
      req.params.id,
      { isActive: false },
      { new: true }
    ).select('-password');

    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    res.json({
      message: 'User deactivated successfully',
      user
    });
  } catch (error) {
    console.error('Deactivate user error:', error);
    res.status(500).json({ error: 'Error deactivating user' });
  }
});

// @route   GET /api/users/stats/overview
// @desc    Get user statistics
// @access  Private (admin only)
router.get('/stats/overview', [auth, authorize('admin')], async (req, res) => {
  try {
    const totalUsers = await User.countDocuments();
    const activeUsers = await User.countDocuments({ isActive: true });
    const verifiedUsers = await User.countDocuments({ isVerified: true });
    
    const usersByRole = await User.aggregate([
      { $group: { _id: '$role', count: { $sum: 1 } } }
    ]);

    res.json({
      stats: {
        total: totalUsers,
        active: activeUsers,
        verified: verifiedUsers,
        byRole: usersByRole
      }
    });
  } catch (error) {
    console.error('Get stats error:', error);
    res.status(500).json({ error: 'Error fetching statistics' });
  }
});

module.exports = router;
