const dns = require('dns');
const { Resolver } = require('dns').promises;

console.log('Testing DNS resolution with different methods...');

// Method 1: Using default resolver
console.log('\nMethod 1: Default resolver');
dns.resolve('google.com', (err, addresses) => {
  if (err) {
    console.log(`FAILED: Default resolver: ${err.message}`);
  } else {
    console.log(`SUCCESS: Default resolver: ${addresses.join(', ')}`);
  }
});

// Method 2: Using system resolver
console.log('\nMethod 2: System resolver');
dns.lookup('google.com', (err, address) => {
  if (err) {
    console.log(`FAILED: System lookup: ${err.message}`);
  } else {
    console.log(`SUCCESS: System lookup: ${address}`);
  }
});

// Method 3: Using custom resolver (Google DNS)
console.log('\nMethod 3: Custom resolver (8.8.8.8)');
const resolver = new Resolver();
resolver.setServers(['8.8.8.8']);
resolver.resolve('google.com').then(addresses => {
  console.log(`SUCCESS: Custom resolver: ${addresses.join(', ')}`);
}).catch(err => {
  console.log(`FAILED: Custom resolver: ${err.message}`);
});

// Method 4: Test MongoDB SRV with custom resolver
console.log('\nMethod 4: MongoDB SRV with custom resolver');
resolver.resolveSrv('_mongodb._tcp.cluster0.zioyfty.mongodb.net').then(records => {
  console.log('SUCCESS: MongoDB SRV resolved:');
  records.forEach(record => {
    console.log(`  - ${record.name}:${record.port}`);
  });
}).catch(err => {
  console.log(`FAILED: MongoDB SRV: ${err.message}`);
});