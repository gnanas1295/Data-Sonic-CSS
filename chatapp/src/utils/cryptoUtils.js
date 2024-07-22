import forge from 'node-forge';
import CryptoJS from 'crypto-js';

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
    const encrypted = publicKey.encrypt(data, 'RSA-OAEP', {
        md: forge.md.sha256.create(),
        mgf1: {
            md: forge.md.sha1.create()
        }
    });
    return forge.util.encode64(encrypted);
};

// Function to decrypt data using RSA private key
export const decryptWithPrivateKey = (encryptedData, privateKeyPem) => {
    const privateKey = forge.pki.privateKeyFromPem(privateKeyPem);
    const decoded = forge.util.decode64(encryptedData);
    const decrypted = privateKey.decrypt(decoded, 'RSA-OAEP', {
        md: forge.md.sha256.create(),
        mgf1: {
            md: forge.md.sha1.create()
        }
    });
    return decrypted;
};

// Function to generate a symmetric key (AES)
export const generateSymmetricKey = () => {
    const key = CryptoJS.lib.WordArray.random(16); // 128-bit key
    return key.toString(CryptoJS.enc.Hex);
};

// Function to encrypt data using a symmetric key (AES)
export const encryptWithSymmetricKey = (data, key) => {
    const iv = CryptoJS.lib.WordArray.random(16);
    const encrypted = CryptoJS.AES.encrypt(data, CryptoJS.enc.Hex.parse(key), {
        iv: iv
    });
    return iv.toString() + encrypted.toString();
};

// Function to decrypt data using a symmetric key
export const decryptWithSymmetricKey = (encryptedData, key) => {
    try {
        const iv = CryptoJS.enc.Hex.parse(encryptedData.slice(0, 32)); // Extract the IV from the beginning of the encrypted data
        const encrypted = encryptedData.slice(32); // Extract the actual encrypted data
        const decrypted = CryptoJS.AES.decrypt(encrypted, CryptoJS.enc.Hex.parse(key), {
            iv: iv
        });
        return decrypted.toString(CryptoJS.enc.Utf8);
    } catch (error) {
        console.error('Error decrypting message:', error);
        throw error;
    }
};
