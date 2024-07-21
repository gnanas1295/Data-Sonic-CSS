import forge from 'node-forge';

// Function to generate RSA key pair
export const generateKeyPair = () => {
    const rsa = forge.pki.rsa.generateKeyPair(2048);
    return {
        publicKey: forge.pki.publicKeyToPem(rsa.publicKey),
        privateKey: forge.pki.privateKeyToPem(rsa.privateKey)
    };
};

// Function to encrypt data using RSA public key
export const encryptWithPublicKey = (data, publicKeyPem) => {
    const publicKey = forge.pki.publicKeyFromPem(publicKeyPem);
    const encrypted = publicKey.encrypt(data, 'RSA-OAEP');
    return forge.util.encode64(encrypted);
};

// Function to decrypt data using RSA private key
export const decryptWithPrivateKey = (encryptedData, privateKeyPem) => {
    const privateKey = forge.pki.privateKeyFromPem(privateKeyPem);
    const decoded = forge.util.decode64(encryptedData);
    const decrypted = privateKey.decrypt(decoded, 'RSA-OAEP');
    return decrypted;
};

// Function to encrypt data using a symmetric key (AES)
export const encryptWithSymmetricKey = (data, key) => {
    const iv = forge.random.getBytesSync(16);
    const cipher = forge.cipher.createCipher('AES-CBC', key);
    cipher.start({ iv: iv });
    cipher.update(forge.util.createBuffer(data));
    cipher.finish();
    const encrypted = cipher.output;
    return forge.util.encode64(iv + encrypted.toHex());
};

// Function to decrypt data using a symmetric key
export const decryptWithSymmetricKey = (encryptedData, key) => {
    const data = forge.util.decode64(encryptedData);
    const iv = data.slice(0, 16);
    const encrypted = data.slice(16);
    const decipher = forge.cipher.createDecipher('AES-CBC', key);
    decipher.start({ iv: iv });
    decipher.update(forge.util.createBuffer(encrypted, 'hex'));
    decipher.finish();
    return decipher.output.toString();
};
