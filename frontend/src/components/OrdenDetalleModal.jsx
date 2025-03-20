// src/components/OrdenDetalleModal.jsx
import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper
} from '@mui/material';

function OrdenDetalleModal({ open, onClose, orden }) {
  if (!orden) return null;
  const detalles = Array.isArray(orden.detalles) ? orden.detalles : [];
  
  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="md">
      <DialogTitle>Detalle de Orden de Compra</DialogTitle>
      <DialogContent dividers>
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle1">
            N° Orden: {orden.numero_orden}
          </Typography>
          <Typography variant="subtitle1">
            Fecha: {orden.fecha ? new Date(orden.fecha).toLocaleDateString() : 'N/A'} - Hora: {orden.fecha ? new Date(orden.fecha).toLocaleTimeString() : 'N/A'}
          </Typography>
          <Typography variant="subtitle1">
            Empresa: {orden.empresa}
          </Typography>
          {orden.proveedor && (
            <>
              <Typography variant="subtitle1">
                Proveedor: {orden.proveedor.nombre_proveedor}
              </Typography>
              <Typography variant="subtitle1">
                Rut: {orden.proveedor.rut}
              </Typography>
              <Typography variant="subtitle1">
                Domicilio: {orden.proveedor.domicilio}
              </Typography>
              <Typography variant="subtitle1">
                Fono: {orden.proveedor.telefono}
              </Typography>
            </>
          )}
          <Typography variant="subtitle1">
            Cargo: {orden.cargo}
          </Typography>
          <Typography variant="subtitle1">
            Forma de Pago: {orden.forma_pago}
          </Typography>
          <Typography variant="subtitle1">
            Plazo de Entrega: {orden.plazo_entrega}
          </Typography>
          <Typography variant="subtitle1">
            Comentarios: {orden.comentarios || 'Ninguno'}
          </Typography>
          <Typography variant="subtitle1">
            Estado: {orden.estado || 'pendiente'}
          </Typography>
        </Box>
        <Box>
          <Typography variant="h6" gutterBottom>
            Detalle de la Orden
          </Typography>
          {detalles.length > 0 ? (
            <TableContainer component={Paper}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Cantidad</TableCell>
                    <TableCell>Producto</TableCell>
                    <TableCell>Precio Unitario</TableCell>
                    <TableCell>Total Producto</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {detalles.map((item, index) => {
                    const cantidad = Number(item.cantidad);
                    const precio = Number(item.precio_unitario);
                    return (
                      <TableRow key={index}>
                        <TableCell>{cantidad}</TableCell>
                        <TableCell>{item.detalle}</TableCell>
                        <TableCell>${precio.toFixed(2)}</TableCell>
                        <TableCell>${(cantidad * precio).toFixed(2)}</TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          ) : (
            <Typography variant="body1">No hay detalles disponibles</Typography>
          )}
        </Box>
        {/* Firmas: Nombres en una fila y líneas debajo */}
        <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-around' }}>
          <Box>
            <Typography variant="subtitle1" align="center">
              Jefe Faena
            </Typography>
            <Typography variant="subtitle2" align="center">
              __________________________
            </Typography>
          </Box>
          <Box>
            <Typography variant="subtitle1" align="center">
              Solicitante
            </Typography>
            <Typography variant="subtitle2" align="center">
              __________________________
            </Typography>
          </Box>
          <Box>
            <Typography variant="subtitle1" align="center">
              Contabilidad
            </Typography>
            <Typography variant="subtitle2" align="center">
              __________________________
            </Typography>
          </Box>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cerrar</Button>
      </DialogActions>
    </Dialog>
  );
}

export default OrdenDetalleModal;
