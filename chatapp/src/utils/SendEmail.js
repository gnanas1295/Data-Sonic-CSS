import { gapi } from 'gapi-script';

const CLIENT_ID = '70768944881-rr2qpncbusabhk5auqf3d12mha7t4dqg.apps.googleusercontent.com';
const API_KEY = 'AIzaSyB1j1FDgZMBfunda8w264eYObOVQNFeudo';
const SCOPES = 'https://www.googleapis.com/auth/gmail.send';

export const sendEmail = async (recipient, subject, body) => {
    try {
        await gapi.load('client:auth2', async () => {
            await gapi.client.init({
                apiKey: API_KEY,
                clientId: CLIENT_ID,
                discoveryDocs: ['https://www.googleapis.com/discovery/v1/apis/gmail/v1/rest'],
                scope: SCOPES,
            });

            const authInstance = gapi.auth2.getAuthInstance();
            await authInstance.signIn();

            const base64EncodedEmail = btoa(
                `Content-Type: text/plain; charset="UTF-8"\n` +
                `MIME-Version: 1.0\n` +
                `Content-Transfer-Encoding: 7bit\n` +
                `to: ${recipient}\n` +
                `subject: ${subject}\n\n` +
                `${body}`
            ).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');

            await gapi.client.gmail.users.messages.send({
                userId: 'me',
                resource: {
                    raw: base64EncodedEmail,
                },
            });
        });

        console.log('Email sent successfully');
    } catch (error) {
        console.error('Error sending email:', error);
    }
};
