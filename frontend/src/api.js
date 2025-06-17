import axios from 'axios';

const api = axios.create({
    baseURL: '',  // Empty baseURL since we're using relative paths
    withCredentials: true,  // Important for handling cookies/sessions
    headers: {
        'Content-Type': 'application/json'
    }
});

export default api; 