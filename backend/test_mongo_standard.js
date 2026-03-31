const mongoose = require('mongoose');

// Standard MongoDB connection string (not SRV)
const mongoUri = 'mongodb://sakshamparadox_db_user:PQtLqvrSvpyBBsEA@ac-ebua8tu-shard-00-00.zioyfty.mongodb.net:27017,ac-ebua8tu-shard-00-01.zioyfty.mongodb.net:27017,ac-ebua8tu-shard-00-02.zioyfty.mongodb.net:27017/Ragblog?ssl=true&replicaSet=atlas-zioyfty-shard-0&authSource=admin&retryWrites=true&w=majority';
const mongoDbName = 'Ragblog';

console.log('Testing MongoDB connection from Node.js with standard URI...');
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