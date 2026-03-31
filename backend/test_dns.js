const dns = require('dns').promises;

async function testDNSResolution() {
  console.log('Testing DNS resolution in Node.js...');
  
  try {
    // Test basic DNS resolution
    const addresses = await dns.resolve('google.com');
    console.log(`SUCCESS: google.com resolves to: ${addresses.join(', ')}`);
  } catch (err) {
    console.log(`FAILED: Cannot resolve google.com: ${err.message}`);
  }
  
  try {
    // Test SRV record resolution
    const srvRecords = await dns.resolveSrv('_mongodb._tcp.cluster0.zioyfty.mongodb.net');
    console.log('SUCCESS: SRV records resolved:');
    srvRecords.forEach(record => {
      console.log(`  - ${record.name}:${record.port} (priority: ${record.priority}, weight: ${record.weight})`);
    });
  } catch (err) {
    console.log(`FAILED: Cannot resolve SRV records: ${err.message}`);
  }
  
  try {
    // Test resolving one of the shard hosts
    const addresses = await dns.resolve('ac-ebua8tu-shard-00-00.zioyfty.mongodb.net');
    console.log(`SUCCESS: ac-ebua8tu-shard-00-00.zioyfty.mongodb.net resolves to: ${addresses.join(', ')}`);
  } catch (err) {
    console.log(`FAILED: Cannot resolve shard host: ${err.message}`);
  }
}

testDNSResolution();