// src/components/SolicitudDetalleModal.jsx
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

function SolicitudDetalleModal({ open, onClose, solicitud }) {
  if (!solicitud) return null;
  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="md">
      <DialogTitle>Detalle de Solicitud</DialogTitle>
      <DialogContent dividers>
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle1">N° Solicitud: {solicitud.numero_solicitud}</Typography>
          <Typography variant="subtitle1">Solicitante: {solicitud.nombre_solicitante}</Typography>
          <Typography variant="subtitle1">
            Fecha: {new Date(solicitud.fecha_creacion).toLocaleDateString()}
          </Typography>
          <Typography variant="subtitle1">Estado: {solicitud.estado}</Typography>
          <Typography variant="subtitle1">Comentario: {solicitud.comentario || 'Ninguno'}</Typography>
        </Box>
        {/* Si existen detalles, mostrarlos en una tabla */}
        {solicitud.detalles && solicitud.detalles.length > 0 ? (
          <TableContainer component={Paper}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Item</TableCell>
                  <TableCell>Cantidad</TableCell>
                  <TableCell>Insumo/Material</TableCell>
                  <TableCell>Motivo</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {solicitud.detalles.map((det, idx) => (
                  <TableRow key={idx}>
                    <TableCell>{idx + 1}</TableCell>
                    <TableCell>{det.cantidad}</TableCell>
                    <TableCell>{det.producto}</TableCell>
                    <TableCell>{det.motivo}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        ) : (
          <Typography variant="body1">No hay detalles</Typography>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cerrar</Button>
      </DialogActions>
    </Dialog>
  );
}

export default SolicitudDetalleModal;
