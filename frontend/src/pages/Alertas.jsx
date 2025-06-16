// src/pages/Alertas.jsx
import React, { useEffect, useState } from 'react';
import {
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Paper, Typography, CircularProgress
} from '@mui/material';
import axiosInstance from '../api/axiosInstance';

const Alertas = () => {
  const [alertas, setAlertas] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
   axiosInstance.get('/bodega/alertas/')
      .then(response => {
        setAlertas(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error al cargar alertas:', error);
        setLoading(false);
      });
  }, []);

  return (
    <Paper sx={{ p: 3, mt: 2 }}>
      <Typography variant="h5" gutterBottom>
        Alertas de Stock Bajo
      </Typography>
      {loading ? (
        <CircularProgress />
      ) : (
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Producto</TableCell>
                <TableCell>Mensaje</TableCell>
                <TableCell>Fecha</TableCell>
                <TableCell>Stock Actual</TableCell>
                <TableCell>Stock Mínimo</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {alertas.map(alerta => (
                <TableRow key={alerta.id}>
                  <TableCell>{alerta.producto.nombre}</TableCell>
                  <TableCell>{alerta.mensaje}</TableCell>
                  <TableCell>{new Date(alerta.fecha).toLocaleString()}</TableCell>
                  <TableCell>{alerta.producto.stock}</TableCell>
                  <TableCell>{alerta.producto.stock_minimo}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Paper>
  );
};

export default Alertas;
