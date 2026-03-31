const { MongoClient } = require('mongodb');
const dns = require('dns');

// Configure Node.js to use Google DNS
dns.setServers(['8.8.8.8', '8.8.4.4']);

console.log('DNS servers configured:', dns.getServers());

const mongoUri = 'mongodb+srv://sakshamparadox_db_user:PQtLqvrSvpyBBsEA@cluster0.zioyfty.mongodb.net/?appName=Cluster0';
const mongoDbName = 'Ragblog';

console.log('Testing MongoDB connection with custom DNS...');
console.log('Database:', mongoDbName);

const client = new MongoClient(mongoUri, {
  serverSelectionTimeoutMS: 10000,
  connectTimeoutMS: 10000,
});

client.connect()
.then(() => {
  console.log('SUCCESS: MongoDB connected!');
  
  const db = client.db(mongoDbName);
  return db.listCollections().toArray();
})
.then((collections) => {
  console.log(`SUCCESS: Found ${collections.length} collections:`);
  collections.forEach(col => {
    console.log(`  - ${col.name}`);
  });
  
  return client.close();
})
.then(() => {
  console.log('SUCCESS: Disconnected successfully');
  process.exit(0);
})
.catch((err) => {
  console.error('FAILED: MongoDB connection failed:', err.message);
  process.exit(1);
});