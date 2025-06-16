import React from 'react';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import InventarioPage from './pages/InventarioPage';
import MovimientosPage from './pages/MovimientosPage';
import Ordenes from './pages/Ordenes';
import Solicitudes from './pages/Solicitiudes';
import Alertas from './pages/Alertas';
import { AuthProvider } from './contexts/AuthContext';


function App() {
  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <AuthProvider>
        <Router>
          <Routes>
            <Route path="/" element={<Login />} />
            <Route path="/dashboard" element={<Dashboard />}>
              <Route path="stock" element={<InventarioPage />} />
              <Route path="movimientos" element={<MovimientosPage />} />
              <Route path="ordenes" element={<Ordenes />} />
              <Route path="solicitudes" element={<Solicitudes />} />
              <Route path="alertas" element={<Alertas />} />
            </Route>
          </Routes>
        </Router>
      </AuthProvider>
    </LocalizationProvider>
  );
}

export default App;
