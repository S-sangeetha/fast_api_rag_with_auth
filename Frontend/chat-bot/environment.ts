const baseUrl = ' http://127.0.0.1:8000';
const webSocket = "ws://127.0.0.1:8000"
export const environment = {
    chatServiceUrl: `${webSocket}/rag/ws`,
    authServiceUrl: `${baseUrl}/auth`,
    uploadServiceUrl: `${baseUrl}/documents/upload`
};  