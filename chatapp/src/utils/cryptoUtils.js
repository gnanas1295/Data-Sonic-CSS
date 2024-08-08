import forge from 'node-forge';
import CryptoJS from 'crypto-js';

// Function to generate RSA key pair
export const generateKeyPair = () => {
    console.log("Coming Here GS Generation of Key Pair 1")
    const rsa = forge.pki.rsa.generateKeyPair(2048);
    console.log("Coming Here GS Generation of Key Pair 2")
    return {
        publicKey: forge.pki.publicKeyToPem(rsa.publicKey),
        privateKey: forge.pki.privateKeyToPem(rsa.privateKey)
    };
};

// Function to encrypt data using RSA public key
export const encryptWithPublicKey = (data, publicKeyPem) => {
    console.log("Coming Here GS Encryption of data using RSA Public Key 1")
    const publicKey = forge.pki.publicKeyFromPem(publicKeyPem);
    const encrypted = publicKey.encrypt(data, 'RSA-OAEP', {
        md: forge.md.sha256.create(),
        mgf1: {
            md: forge.md.sha1.create()
        }
    });
    console.log("Coming Here GS Encryption of data using RSA Public Key 2")
    return forge.util.encode64(encrypted);
};

// Function to decrypt data using RSA private key
export const decryptWithPrivateKey = (encryptedData, privateKeyPem) => {
    console.log("Coming Here GS Decryption of data using RSA Private Key 1")
    const privateKey = forge.pki.privateKeyFromPem(privateKeyPem);
    const decoded = forge.util.decode64(encryptedData);
    const decrypted = privateKey.decrypt(decoded, 'RSA-OAEP', {
        md: forge.md.sha256.create(),
        mgf1: {
            md: forge.md.sha1.create()
        }
    });
    console.log("Coming Here GS Decryption of data using RSA Private Key 2")
    return decrypted;
};

// Function to generate a symmetric key (AES)
export const generateSymmetricKey = () => {
    console.log("Coming Here GS Generation of Symmetric Key 1")
    const key = CryptoJS.lib.WordArray.random(16); // 128-bit key
    console.log("Coming Here GS Generation of Symmetric Key 2")
    return key.toString(CryptoJS.enc.Hex);
};

// Function to encrypt data using a symmetric key (AES)
export const encryptWithSymmetricKey = (data, key) => {
    console.log("Coming Here GS Encryption of data using Symmetric Key 1")
    const iv = CryptoJS.lib.WordArray.random(16);
    const encrypted = CryptoJS.AES.encrypt(data, CryptoJS.enc.Hex.parse(key), {
        iv: iv
    });
    console.log("Coming Here GS Encryption of data using Symmetric Key 2")
    return iv.toString() + encrypted.toString();
};

// Function to decrypt data using a symmetric key
// export const decryptWithSymmetricKey = (encryptedData, key) => {
//     try {
//         const iv = CryptoJS.enc.Hex.parse(encryptedData.slice(0, 32)); // Extract the IV from the beginning of the encrypted data
//         const encrypted = encryptedData.slice(32); // Extract the actual encrypted data
//         const decrypted = CryptoJS.AES.decrypt(encrypted, CryptoJS.enc.Hex.parse(key), {
//             iv: iv
//         });
//         return decrypted.toString(CryptoJS.enc.Utf8);
//     } catch (error) {
//         console.error('Error decrypting message:', error);
//         throw error;
//     }
// };

// Function to decrypt data using a symmetric key
export const decryptWithSymmetricKey = (encryptedData, key) => {
    try {
        console.log("Coming Here GS Decryption of data using Symmetric Key 1")
        const ivLength = 32; 
        const ivHex = encryptedData.slice(0, ivLength);
        const encrypted = encryptedData.slice(ivLength);
        const iv = CryptoJS.enc.Hex.parse(ivHex);
        const decrypted = CryptoJS.AES.decrypt(encrypted, CryptoJS.enc.Hex.parse(key), { iv: iv });
        console.log("Coming Here GS Decryption of data using Symmetric Key 2")
        return decrypted.toString(CryptoJS.enc.Utf8);
    } catch (error) {
        console.error('Error decrypting message:', error);
        throw error;
    }
};
