import axios from 'axios';

const api = axios.create({
    baseURL: '/api',  // This will be relative to the current domain
    withCredentials: true,  // Important for handling cookies/sessions
    headers: {
        'Content-Type': 'application/json'
    }
});

export default api; 