const mongoose = require('mongoose');
const path = require('path');
const fs = require('fs');

// Read .env file
const envPath = path.join(__dirname, '../.env');
const envContent = fs.readFileSync(envPath, 'utf8');

// Parse MONGO_URI from .env
const mongoUriMatch = envContent.match(/MONGO_URI=(.+)/);
const mongoDbNameMatch = envContent.match(/MONGO_DB_NAME=(.+)/);

if (!mongoUriMatch || !mongoDbNameMatch) {
  console.error('Could not find MONGO_URI or MONGO_DB_NAME in .env file');
  process.exit(1);
}

const mongoUri = mongoUriMatch[1].trim();
const mongoDbName = mongoDbNameMatch[1].trim();

console.log('Testing MongoDB connection from Node.js...');
console.log('URI:', mongoUri);
console.log('Database:', mongoDbName);

mongoose.connect(mongoUri, {
  dbName: mongoDbName,
  serverSelectionTimeoutMS: 5000,
})
.then(() => {
  console.log('✓ MongoDB connected successfully!');
  
  // List collections
  return mongoose.connection.db.listCollections().toArray();
})
.then((collections) => {
  console.log(`✓ Found ${collections.length} collections:`);
  collections.forEach(col => {
    console.log(`  - ${col.name}`);
  });
  
  return mongoose.disconnect();
})
.then(() => {
  console.log('✓ Disconnected successfully');
  process.exit(0);
})
.catch((err) => {
  console.error('✗ MongoDB connection failed:', err.message);
  process.exit(1);
});