// src/components/NuevaSolicitudModal.jsx
import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Typography
} from '@mui/material';

function NuevaSolicitudModal({ open, onClose, onSubmit }) {
  const [nombreSolicitante, setNombreSolicitante] = useState('');
  const [folio, setFolio] = useState('');
  const [comentario, setComentario] = useState('');
  // Se añade el campo stockBodega para cada detalle
  const [detalleItems, setDetalleItems] = useState([
    { producto: '', cantidad: '', cargo: '', stockBodega: '' },
  ]);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (open) {
      setErrors({});
    }
  }, [open]);

  const validateForm = () => {
    const errs = {};
    if (!nombreSolicitante) {
      errs.nombreSolicitante = "El nombre del solicitante es obligatorio";
    }
    if (!folio) {
      errs.folio = "El número de folio es obligatorio";
    }
    const detallesErrors = detalleItems.map(item => {
      const itemErr = {};
      if (!item.producto) {
        itemErr.producto = "Ingrese el insumo/material";
      }
      if (!item.cantidad || parseFloat(item.cantidad) <= 0) {
        itemErr.cantidad = "La cantidad debe ser mayor a 0";
      }
      if (!item.cargo) {
        itemErr.cargo = "El cargo es obligatorio";
      }
      if (item.stockBodega === '' || parseFloat(item.stockBodega) < 0) {
        itemErr.stockBodega = "El stock en bodega es obligatorio y debe ser mayor o igual a 0";
      }
      return itemErr;
    });
    if (detallesErrors.some(e => Object.keys(e).length > 0)) {
      errs.detalleItems = detallesErrors;
    }
    return errs;
  };

  const handleAddDetalle = () => {
    setDetalleItems([
      ...detalleItems,
      { producto: '', cantidad: '', cargo: '', stockBodega: '' },
    ]);
  };

  const handleRemoveDetalle = (index) => {
    const newDetails = [...detalleItems];
    newDetails.splice(index, 1);
    setDetalleItems(newDetails);
  };

  const handleSubmit = () => {
    const errs = validateForm();
    setErrors(errs);
    if (Object.keys(errs).length === 0) {
      // Mapeamos "cargo" a "motivo" en el payload, ya que el serializer espera "motivo"
      const payload = {
        nombre_solicitante: nombreSolicitante,
        folio: folio,
        comentario: comentario,
        detalles: detalleItems.map(item => ({
          producto: item.producto,
          cantidad: parseFloat(item.cantidad),
          motivo: item.cargo,  // Aquí asignamos el valor de "cargo" al campo "motivo"
          stock_bodega: parseFloat(item.stockBodega),
        })),
      };
      onSubmit(payload);
      // Resetear formulario
      setNombreSolicitante('');
      setFolio('');
      setComentario('');
      setDetalleItems([{ producto: '', cantidad: '', cargo: '', stockBodega: '' }]);
      setErrors({});
    }
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>Nueva Solicitud</DialogTitle>
      <DialogContent>
        <Box sx={{ mt: 2 }}>
          <TextField
            autoFocus
            label="Nombre del Solicitante"
            fullWidth
            variant="standard"
            value={nombreSolicitante}
            onChange={(e) => setNombreSolicitante(e.target.value)}
            error={Boolean(errors.nombreSolicitante)}
            helperText={errors.nombreSolicitante}
          />
        </Box>
        <Box sx={{ mt: 2 }}>
          <TextField
            label="Número de Folio"
            fullWidth
            variant="standard"
            value={folio}
            onChange={(e) => setFolio(e.target.value)}
            error={Boolean(errors.folio)}
            helperText={errors.folio}
          />
        </Box>
        <Box sx={{ mt: 2 }}>
          <TextField
            label="Comentario"
            fullWidth
            variant="standard"
            multiline
            rows={3}
            value={comentario}
            onChange={(e) => setComentario(e.target.value)}
            error={Boolean(errors.comentario)}
            helperText={errors.comentario}
          />
        </Box>
        <Box sx={{ mt: 3 }}>
          <Typography variant="h6">Detalles de la Solicitud</Typography>
          {detalleItems.map((item, index) => (
            <Box key={index} sx={{ display: 'flex', gap: 2, mt: 2, alignItems: 'center' }}>
              <TextField
                label="Insumo/Material"
                variant="standard"
                value={item.producto}
                onChange={(e) => {
                  const newDetails = [...detalleItems];
                  newDetails[index].producto = e.target.value;
                  setDetalleItems(newDetails);
                }}
                fullWidth
                error={
                  errors.detalleItems &&
                  errors.detalleItems[index] &&
                  Boolean(errors.detalleItems[index].producto)
                }
                helperText={
                  errors.detalleItems &&
                  errors.detalleItems[index] &&
                  errors.detalleItems[index].producto
                }
              />
              <TextField
                label="Cantidad"
                type="number"
                variant="standard"
                value={item.cantidad}
                onChange={(e) => {
                  const newDetails = [...detalleItems];
                  newDetails[index].cantidad = e.target.value;
                  setDetalleItems(newDetails);
                }}
                error={
                  errors.detalleItems &&
                  errors.detalleItems[index] &&
                  Boolean(errors.detalleItems[index].cantidad)
                }
                helperText={
                  errors.detalleItems &&
                  errors.detalleItems[index] &&
                  errors.detalleItems[index].cantidad
                }
              />
              <TextField
                label="Cargo"
                variant="standard"
                value={item.cargo}
                onChange={(e) => {
                  const newDetails = [...detalleItems];
                  newDetails[index].cargo = e.target.value;
                  setDetalleItems(newDetails);
                }}
                fullWidth
                error={
                  errors.detalleItems &&
                  errors.detalleItems[index] &&
                  Boolean(errors.detalleItems[index].cargo)
                }
                helperText={
                  errors.detalleItems &&
                  errors.detalleItems[index] &&
                  errors.detalleItems[index].cargo
                }
              />
              <TextField
                label="Stock en Bodega"
                type="number"
                variant="standard"
                value={item.stockBodega}
                onChange={(e) => {
                  const newDetails = [...detalleItems];
                  newDetails[index].stockBodega = e.target.value;
                  setDetalleItems(newDetails);
                }}
                error={
                  errors.detalleItems &&
                  errors.detalleItems[index] &&
                  Boolean(errors.detalleItems[index].stockBodega)
                }
                helperText={
                  errors.detalleItems &&
                  errors.detalleItems[index] &&
                  errors.detalleItems[index].stockBodega
                }
              />
              <Button variant="outlined" color="error" onClick={() => handleRemoveDetalle(index)}>
                Eliminar
              </Button>
            </Box>
          ))}
          <Button variant="outlined" onClick={handleAddDetalle} sx={{ mt: 2 }}>
            Agregar Insumo
          </Button>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancelar</Button>
        <Button onClick={handleSubmit} variant="contained">
          Crear Solicitud
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export default NuevaSolicitudModal;
