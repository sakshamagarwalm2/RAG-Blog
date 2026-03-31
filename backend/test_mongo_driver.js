const { MongoClient } = require('mongodb');

// Standard MongoDB connection string (not SRV)
const mongoUri = 'mongodb://sakshamparadox_db_user:PQtLqvrSvpyBBsEA@ac-ebua8tu-shard-00-00.zioyfty.mongodb.net:27017,ac-ebua8tu-shard-00-01.zioyfty.mongodb.net:27017,ac-ebua8tu-shard-00-02.zioyfty.mongodb.net:27017/Ragblog?ssl=true&replicaSet=atlas-zioyfty-shard-0&authSource=admin&retryWrites=true&w=majority';
const mongoDbName = 'Ragblog';

console.log('Testing MongoDB connection from Node.js with mongodb driver...');
console.log('Database:', mongoDbName);

const client = new MongoClient(mongoUri, {
  serverSelectionTimeoutMS: 5000,
  connectTimeoutMS: 5000,
});

client.connect()
.then(() => {
  console.log('✓ MongoDB connected successfully!');
  
  const db = client.db(mongoDbName);
  return db.listCollections().toArray();
})
.then((collections) => {
  console.log(`✓ Found ${collections.length} collections:`);
  collections.forEach(col => {
    console.log(`  - ${col.name}`);
  });
  
  return client.close();
})
.then(() => {
  console.log('✓ Disconnected successfully');
  process.exit(0);
})
.catch((err) => {
  console.error('✗ MongoDB connection failed:', err.message);
  console.error('Full error:', err);
  process.exit(1);
});