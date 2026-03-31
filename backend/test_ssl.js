const tls = require('tls');
const net = require('net');

function testSSLConnection(host, port) {
  return new Promise((resolve, reject) => {
    console.log(`Testing SSL connection to ${host}:${port}...`);
    
    const socket = tls.connect({
      host: host,
      port: port,
      rejectUnauthorized: false, // Allow self-signed certificates for testing
      timeout: 5000
    }, () => {
      console.log(`SUCCESS: SSL connection established to ${host}:${port}`);
      socket.end();
      resolve(true);
    });
    
    socket.on('error', (err) => {
      console.log(`FAILED: SSL connection failed to ${host}:${port}: ${err.message}`);
      reject(err);
    });
    
    socket.on('timeout', () => {
      console.log(`FAILED: SSL connection timeout to ${host}:${port}`);
      socket.destroy();
      reject(new Error('Timeout'));
    });
  });
}

async function main() {
  const shards = [
    'ac-ebua8tu-shard-00-00.zioyfty.mongodb.net',
    'ac-ebua8tu-shard-00-01.zioyfty.mongodb.net',
    'ac-ebua8tu-shard-00-02.zioyfty.mongodb.net'
  ];
  
  let allSuccess = true;
  
  for (const shard of shards) {
    try {
      await testSSLConnection(shard, 27017);
    } catch (err) {
      allSuccess = false;
    }
  }
  
  if (allSuccess) {
    console.log('\nSUCCESS: All MongoDB shards are reachable via SSL');
  } else {
    console.log('\nFAILED: Some MongoDB shards are not reachable via SSL');
    process.exit(1);
  }
}

main();