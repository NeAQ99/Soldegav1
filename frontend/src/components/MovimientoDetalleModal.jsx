// src/components/MovimientoDetalleModal.jsx
import React from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Typography, Box } from '@mui/material';

function MovimientoDetalleModal({ open, onClose, movimiento }) {
  if (!movimiento) return null;

  const productoInfo = movimiento.producto_info ||
    (movimiento.producto && movimiento.producto.codigo && movimiento.producto.nombre
      ? `${movimiento.producto.codigo} - ${movimiento.producto.nombre}`
      : movimiento.producto);

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>Detalle del Movimiento</DialogTitle>
      <DialogContent dividers>
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle1">Producto: {productoInfo}</Typography>
          <Typography variant="subtitle1">Cantidad: {movimiento.cantidad}</Typography>
          <Typography variant="subtitle1">Tipo: {movimiento.motivo || movimiento.cargo}</Typography>
          <Typography variant="subtitle1">Fecha: {new Date(movimiento.fecha).toLocaleDateString()}</Typography>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} variant="contained">Cerrar</Button>
      </DialogActions>
    </Dialog>
  );
}

export default MovimientoDetalleModal;
