import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import './styles/dashboard.css';
import './styles/results.css';
createRoot(document.getElementById('root')!).render(<React.StrictMode><App /></React.StrictMode>);
