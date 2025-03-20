import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
  Autocomplete,
} from '@mui/material';
import EquiposModal from './EquiposModal';

const CARGO_OPTIONS = [
  'maquinaria',
  'taller',
  'bodega',
  'gerencia',
  'insumos de bodega',
  'otros',
];

function SalidaModal({ open, onClose, onSubmit, productos }) {
  const [salidaItems, setSalidaItems] = useState([{ producto: null, cantidad: '', cargo: '' }]);
  const [comentario, setComentario] = useState('');
  const [errors, setErrors] = useState({});
  // Nuevo estado para el equipo de maquinaria seleccionado
  const [selectedMaquinaria, setSelectedMaquinaria] = useState(null);
  const [openEquiposModal, setOpenEquiposModal] = useState(false);

  const validateItem = (item) => {
    const itemErrors = {};
    if (!item.producto) {
      itemErrors.producto = 'Debe seleccionar un producto';
    }
    if (!item.cantidad || parseFloat(item.cantidad) <= 0) {
      itemErrors.cantidad = 'La cantidad debe ser mayor a 0 (ej: 5)';
    }
    if (!item.cargo) {
      itemErrors.cargo = 'Debe seleccionar un cargo';
    }
    // Si el cargo es "maquinaria", verificar que se haya seleccionado un equipo
    if (item.cargo === 'maquinaria' && !selectedMaquinaria) {
      itemErrors.cargo = 'Debe seleccionar un equipo de maquinaria';
    }
    return itemErrors;
  };

  const validateForm = () => {
    const formErrors = {};
    const itemsErrors = salidaItems.map(validateItem);
    if (itemsErrors.some((err) => Object.keys(err).length > 0)) {
      formErrors.items = itemsErrors;
    }
    return formErrors;
  };

  const handleAddItem = () => {
    setSalidaItems([...salidaItems, { producto: null, cantidad: '', cargo: '' }]);
  };

  const handleRemoveItem = (index) => {
    const newItems = [...salidaItems];
    newItems.splice(index, 1);
    setSalidaItems(newItems);
  };

  const handleSubmit = () => {
    const validationErrors = validateForm();
    setErrors(validationErrors);
    if (Object.keys(validationErrors).length === 0) {
      const payload = {
        items: salidaItems.map((item) => ({
          producto: item.producto ? item.producto.id : null,
          cantidad: item.cantidad,
          cargo: item.cargo,
          // Incluir el ID del equipo si el cargo es "maquinaria"
          maquinaria: item.cargo === 'maquinaria' && selectedMaquinaria ? selectedMaquinaria.id : null,
        })),
        comentario,
      };
      onSubmit(payload);
      setSalidaItems([{ producto: null, cantidad: '', cargo: '' }]);
      setComentario('');
      setErrors({});
      setSelectedMaquinaria(null);
    }
  };

  useEffect(() => {
    if (open) setErrors({});
  }, [open]);

  return (
    <Dialog open={open} onClose={onClose} fullWidth>
      <DialogTitle>Registrar Salida</DialogTitle>
      <DialogContent>
        {salidaItems.map((item, index) => (
          <Box key={index} sx={{ display: 'flex', gap: 2, mb: 2, alignItems: 'center' }}>
            <Autocomplete
              options={productos}
              getOptionLabel={(option) => `${option.codigo} - ${option.nombre}`}
              value={item.producto}
              onChange={(event, newValue) => {
                const newItems = [...salidaItems];
                newItems[index].producto = newValue;
                setSalidaItems(newItems);
              }}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Producto"
                  variant="standard"
                  error={errors.items && errors.items[index] && Boolean(errors.items[index].producto)}
                  helperText={errors.items && errors.items[index] && errors.items[index].producto}
                />
              )}
              fullWidth
            />
            <TextField
              label="Cantidad"
              type="number"
              variant="standard"
              value={item.cantidad}
              onChange={(e) => {
                const newItems = [...salidaItems];
                newItems[index].cantidad = e.target.value;
                setSalidaItems(newItems);
              }}
              error={errors.items && errors.items[index] && Boolean(errors.items[index].cantidad)}
              helperText={errors.items && errors.items[index] && errors.items[index].cantidad}
            />
            <FormControl variant="standard" fullWidth error={errors.items && errors.items[index] && Boolean(errors.items[index].cargo)}>
              <InputLabel id={`cargo-label-${index}`}>Cargo</InputLabel>
              <Select
                labelId={`cargo-label-${index}`}
                value={item.cargo}
                label="Cargo"
                onChange={(e) => {
                  const newItems = [...salidaItems];
                  newItems[index].cargo = e.target.value;
                  setSalidaItems(newItems);
                  // Si el cargo seleccionado es "maquinaria", abrir el modal para seleccionar el equipo
                  if (e.target.value === 'maquinaria') {
                    setOpenEquiposModal(true);
                  } else {
                    setSelectedMaquinaria(null);
                  }
                }}
              >
                {CARGO_OPTIONS.map((option) => (
                  <MenuItem key={option} value={option}>
                    {option}
                  </MenuItem>
                ))}
              </Select>
              {errors.items && errors.items[index] && errors.items[index].cargo && (
                <Typography variant="caption" color="error">
                  {errors.items[index].cargo}
                </Typography>
              )}
            </FormControl>
            <Button variant="outlined" color="error" onClick={() => handleRemoveItem(index)}>
              Eliminar
            </Button>
          </Box>
        ))}
        {selectedMaquinaria && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle1">
              Equipo Seleccionado: {selectedMaquinaria.nro_equipo} - {selectedMaquinaria.tipo} - {selectedMaquinaria.patente}
            </Typography>
          </Box>
        )}
        <Button variant="outlined" onClick={handleAddItem}>
          Agregar Producto
        </Button>
        <TextField
          margin="dense"
          label="Comentario"
          fullWidth
          variant="standard"
          multiline
          rows={3}
          value={comentario}
          onChange={(e) => setComentario(e.target.value)}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancelar</Button>
        <Button onClick={handleSubmit}>Registrar</Button>
      </DialogActions>
      <EquiposModal
        open={openEquiposModal}
        onClose={() => setOpenEquiposModal(false)}
        onSelect={(equipo) => {
          setSelectedMaquinaria(equipo);
          setOpenEquiposModal(false);
        }}
      />
    </Dialog>
  );
}

export default SalidaModal;
