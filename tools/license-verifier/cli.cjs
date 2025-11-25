// tools/license-verifier/cli.cjs
const fs = require('fs');
const crypto = require('crypto');
const { machineIdSync } = require('node-machine-id');

function stableString(obj) {
  const subset = {
    machineId: obj.machineId,
    username: obj.username,
    issuedAt: obj.issuedAt,
    expiresAt: obj.expiresAt
  };
  return JSON.stringify(subset);
}

function verifyLicense(licensePath, pubKeyPath, expectedMachineId) {
  const raw = fs.readFileSync(licensePath, 'utf8');
  const lic = JSON.parse(raw);

  if (!lic.machineId || !lic.signature) {
    throw new Error('Invalid license schema.');
  }
  if (lic.machineId !== expectedMachineId) {
    throw new Error('This license is for a different machine.');
  }
  if (lic.expiresAt) {
    const now = Date.now();
    const exp = Date.parse(lic.expiresAt);
    if (!Number.isNaN(exp) && now > exp) {
      throw new Error('License has expired.');
    }
  }

  const publicKey = fs.readFileSync(pubKeyPath);
  const verifier = crypto.createVerify('RSA-SHA256');
  verifier.update(stableString(lic));
  verifier.end();

  const sigBuf = Buffer.from(lic.signature, 'hex');
  const ok = verifier.verify(publicKey, sigBuf);
  if (!ok) throw new Error('Signature verification failed.');
  return true;
}

function printMachineId() {
  const id = machineIdSync({ original: true });
  process.stdout.write(id);
}

function usage() {
  console.log(`
Usage:
  license-verifier.exe --print-machine-id
  license-verifier.exe --verify --license "<path>" --pub "<public_key.bin>"
`);
}

function main() {
  const args = process.argv.slice(2);

  if (args.includes('--print-machine-id')) {
    printMachineId();
    process.exit(0);
  }

  if (args.includes('--verify')) {
    const licIdx = args.indexOf('--license');
    const pubIdx = args.indexOf('--pub');
    if (licIdx === -1 || pubIdx === -1 || !args[licIdx + 1] || !args[pubIdx + 1]) {
      console.error('Missing --license or --pub.');
      process.exit(2);
    }
    const licensePath = args[licIdx + 1];
    const pubPath = args[pubIdx + 1];
    try {
      const expectedMachineId = machineIdSync({ original: true });
      verifyLicense(licensePath, pubPath, expectedMachineId);
      console.log('OK');
      process.exit(0);
    } catch (e) {
      console.error(String(e.message || e));
      process.exit(1);
    }
  }

  usage();
  process.exit(2);
}

main();
