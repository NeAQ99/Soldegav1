// src/components/OrdenesModal.jsx
import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
  DialogActions,
  Button,
  Box,
  Typography
} from '@mui/material';
import axiosInstance from '../api/axiosInstance';

function OrdenesModal({ open, onClose, onSelect }) {
  const [ordenes, setOrdenes] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchOrdenesPendientes = async () => {
    setLoading(true);
    try {
      // Usamos el endpoint creado para obtener órdenes pendientes
      const response = await axiosInstance.get('ordenes/pendientes/');
      setOrdenes(response.data);
    } catch (error) {
      console.error("Error al cargar órdenes pendientes:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (open) {
      fetchOrdenesPendientes();
    }
  }, [open]);

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>Seleccionar OC Pendiente</DialogTitle>
      <DialogContent dividers>
        {loading ? (
          <Box sx={{ textAlign: 'center', p: 2 }}>
            <CircularProgress />
          </Box>
        ) : ordenes.length > 0 ? (
          <List>
            {ordenes.map((oc) => (
              <ListItem button key={oc.id} onClick={() => onSelect(oc)}>
                <ListItemText
                  primary={`OC N° ${oc.numero_orden} - ${oc.empresa}`}
                  secondary={`Estado: ${oc.estado}`}
                />
              </ListItem>
            ))}
          </List>
        ) : (
          <Typography variant="body1">No hay órdenes pendientes disponibles.</Typography>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cerrar</Button>
      </DialogActions>
    </Dialog>
  );
}

export default OrdenesModal;
