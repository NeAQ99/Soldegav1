import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
  Box,
  Typography
} from '@mui/material';
import axiosInstance from '../api/axiosInstance';

function EquiposModal({ open, onClose, onSelect }) {
  const [equipos, setEquipos] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (open) {
      axiosInstance.get('maquinaria/') // Asegúrate de que la ruta sea la correcta
        .then(response => {
          setEquipos(response.data);
          setLoading(false);
        })
        .catch(err => {
          console.error("Error al cargar maquinaria:", err);
          setLoading(false);
        });
    }
  }, [open]);

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>Seleccionar Equipo de Maquinaria</DialogTitle>
      <DialogContent dividers>
        {loading ? (
          <Box sx={{ textAlign: 'center', p: 2 }}>
            <CircularProgress />
          </Box>
        ) : equipos.length > 0 ? (
          <List>
            {equipos.map((equipo) => (
              <ListItem button key={equipo.id} onClick={() => onSelect(equipo)}>
                <ListItemText
                  primary={`Equipo N°: ${equipo.nro_equipo}`}
                  secondary={`Tipo: ${equipo.tipo} - Patente: ${equipo.patente}`}
                />
              </ListItem>
            ))}
          </List>
        ) : (
          <Typography variant="body1">No hay equipos registrados.</Typography>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cerrar</Button>
      </DialogActions>
    </Dialog>
  );
}

export default EquiposModal;
