require('dotenv').config();
const mongoose = require('mongoose');
const User = require('../models/User');
const Venue = require('../models/Venue');
const Event = require('../models/Event');
const Booking = require('../models/Booking');

const seedData = async () => {
  try {
    // Connect to database
    await mongoose.connect(process.env.MONGO_URI);
    console.log('✓ Connected to MongoDB');

    // Clear existing data
    await User.deleteMany({});
    await Venue.deleteMany({});
    await Event.deleteMany({});
    await Booking.deleteMany({});
    console.log('✓ Cleared existing data');

    // Create users
    const users = await User.create([
      {
        name: 'Admin User',
        email: 'admin@eventplatform.com',
        password: 'admin123',
        role: 'admin',
        phone: '+1-555-0001',
        isVerified: true
      },
      {
        name: 'John Venue Owner',
        email: 'john@venues.com',
        password: 'password123',
        role: 'venue_owner',
        phone: '+1-555-0002',
        isVerified: true
      },
      {
        name: 'Jane Event Organizer',
        email: 'jane@events.com',
        password: 'password123',
        role: 'user',
        phone: '+1-555-0003',
        isVerified: true
      },
      {
        name: 'Mike Customer',
        email: 'mike@customer.com',
        password: 'password123',
        role: 'user',
        phone: '+1-555-0004',
        isVerified: true
      }
    ]);
    console.log('✓ Created users');

    // Create venues
    const venues = await Venue.create([
      {
        name: 'Grand Plaza Convention Center',
        description: 'A spacious convention center perfect for large-scale conferences and exhibitions. Features state-of-the-art AV equipment and multiple breakout rooms.',
        owner: users[1]._id,
        location: {
          address: '123 Main Street',
          city: 'New York',
          state: 'NY',
          zipCode: '10001',
          country: 'USA',
          coordinates: { latitude: 40.7589, longitude: -73.9851 }
        },
        capacity: 500,
        pricePerHour: 500,
        amenities: ['WiFi', 'AV Equipment', 'Parking', 'Catering', 'Accessibility'],
        venueType: 'conference',
        images: ['https://example.com/venue1.jpg'],
        rating: 4.8,
        reviewCount: 45
      },
      {
        name: 'Sunset Garden Pavilion',
        description: 'Beautiful outdoor venue with stunning garden views. Perfect for weddings, receptions, and outdoor celebrations.',
        owner: users[1]._id,
        location: {
          address: '456 Garden Lane',
          city: 'Los Angeles',
          state: 'CA',
          zipCode: '90001',
          country: 'USA',
          coordinates: { latitude: 34.0522, longitude: -118.2437 }
        },
        capacity: 200,
        pricePerHour: 350,
        amenities: ['WiFi', 'Outdoor Space', 'Parking', 'Catering', 'Garden'],
        venueType: 'wedding',
        images: ['https://example.com/venue2.jpg'],
        rating: 4.9,
        reviewCount: 78
      },
      {
        name: 'Metro Music Hall',
        description: 'Premier concert venue with professional sound system and lighting. Ideal for concerts, performances, and music events.',
        owner: users[1]._id,
        location: {
          address: '789 Music Boulevard',
          city: 'Nashville',
          state: 'TN',
          zipCode: '37201',
          country: 'USA',
          coordinates: { latitude: 36.1627, longitude: -86.7816 }
        },
        capacity: 1000,
        pricePerHour: 750,
        amenities: ['Sound System', 'Stage Lighting', 'Green Room', 'Bar', 'Parking'],
        venueType: 'concert',
        images: ['https://example.com/venue3.jpg'],
        rating: 4.7,
        reviewCount: 92
      },
      {
        name: 'Corporate Tower Meeting Rooms',
        description: 'Professional meeting spaces in downtown business district. Multiple room sizes available for corporate events and meetings.',
        owner: users[1]._id,
        location: {
          address: '321 Business Park Drive',
          city: 'Chicago',
          state: 'IL',
          zipCode: '60601',
          country: 'USA',
          coordinates: { latitude: 41.8781, longitude: -87.6298 }
        },
        capacity: 50,
        pricePerHour: 150,
        amenities: ['WiFi', 'Projector', 'Whiteboard', 'Coffee Service', 'Accessibility'],
        venueType: 'corporate',
        images: ['https://example.com/venue4.jpg'],
        rating: 4.6,
        reviewCount: 34
      }
    ]);
    console.log('✓ Created venues');

    // Create events
    const futureDate1 = new Date();
    futureDate1.setDate(futureDate1.getDate() + 30);
    const futureDate2 = new Date();
    futureDate2.setDate(futureDate2.getDate() + 45);

    const events = await Event.create([
      {
        title: 'Tech Innovation Summit 2026',
        description: 'Annual technology conference featuring industry leaders and cutting-edge innovations.',
        organizer: users[2]._id,
        venue: venues[0]._id,
        eventType: 'conference',
        startDate: futureDate1,
        endDate: new Date(futureDate1.getTime() + 8 * 60 * 60 * 1000), // 8 hours
        expectedAttendees: 300,
        ticketPrice: 299,
        totalCost: 4000,
        status: 'confirmed',
        isPublic: true,
        tags: ['technology', 'innovation', 'business']
      },
      {
        title: 'Summer Wedding Celebration',
        description: 'Beautiful outdoor wedding ceremony and reception.',
        organizer: users[3]._id,
        venue: venues[1]._id,
        eventType: 'wedding',
        startDate: futureDate2,
        endDate: new Date(futureDate2.getTime() + 6 * 60 * 60 * 1000), // 6 hours
        expectedAttendees: 150,
        ticketPrice: 0,
        totalCost: 2100,
        status: 'pending',
        isPublic: false,
        tags: ['wedding', 'celebration']
      }
    ]);
    console.log('✓ Created events');

    // Create bookings
    const bookingDate = new Date();
    bookingDate.setDate(bookingDate.getDate() + 15);

    await Booking.create([
      {
        user: users[2]._id,
        venue: venues[0]._id,
        event: events[0]._id,
        startDate: futureDate1,
        endDate: new Date(futureDate1.getTime() + 8 * 60 * 60 * 1000),
        duration: 8,
        totalAmount: 4000,
        status: 'confirmed',
        paymentStatus: 'paid',
        paymentMethod: 'credit_card',
        guests: 300,
        transactionId: 'TXN-' + Date.now()
      },
      {
        user: users[3]._id,
        venue: venues[1]._id,
        event: events[1]._id,
        startDate: futureDate2,
        endDate: new Date(futureDate2.getTime() + 6 * 60 * 60 * 1000),
        duration: 6,
        totalAmount: 2100,
        status: 'pending',
        paymentStatus: 'pending',
        paymentMethod: 'credit_card',
        guests: 150,
        specialRequests: 'Vegan catering options required'
      }
    ]);
    console.log('✓ Created bookings');

    console.log('\n✅ Database seeded successfully!\n');
    console.log('Test Users:');
    console.log('  Admin: admin@eventplatform.com / admin123');
    console.log('  Venue Owner: john@venues.com / password123');
    console.log('  Organizer: jane@events.com / password123');
    console.log('  Customer: mike@customer.com / password123\n');

    await mongoose.connection.close();
    process.exit(0);
  } catch (error) {
    console.error('❌ Error seeding database:', error);
    await mongoose.connection.close();
    process.exit(1);
  }
};

seedData();
