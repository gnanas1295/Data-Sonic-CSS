export const base64urlEncode = (str) => {
    // Convert to a Uint8Array
    const utf8Bytes = new TextEncoder().encode(str);
    // Convert to base64
    const base64Str = btoa(String.fromCharCode(...utf8Bytes));
    // Convert to base64url (replace + with -, / with _ and remove padding =)
    return base64Str.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
};
