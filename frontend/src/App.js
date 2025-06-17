import React, { useState, useEffect } from 'react';
import './App.css';
import api from './api';

function App() {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        // Check if user is logged in
        api.get('/check-auth')
            .then(response => {
                setIsLoggedIn(response.data.isLoggedIn);
            })
            .catch(err => {
                console.error('Auth check failed:', err);
                setError('Failed to check authentication status');
            });
    }, []);

    return (
        <div className="App">
            <header className="App-header">
                <h1>Budget Helper</h1>
                {error && <div className="error-message">{error}</div>}
                {isLoggedIn ? (
                    <div>
                        <p>Welcome back! You are logged in.</p>
                        <button onClick={() => api.post('/logout').then(() => setIsLoggedIn(false))}>
                            Logout
                        </button>
                    </div>
                ) : (
                    <div>
                        <p>Welcome to your personal budget management tool</p>
                        <p>Please log in to continue</p>
                    </div>
                )}
            </header>
        </div>
    );
}

export default App; 