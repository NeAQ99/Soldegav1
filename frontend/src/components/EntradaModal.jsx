// src/components/EntradaModal.jsx
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
  Checkbox,
  FormControlLabel,
} from '@mui/material';
import Autocomplete from '@mui/material/Autocomplete';
import axiosInstance from '../api/axiosInstance';
import OrdenesModal from './OrdenesModal';

function EntradaModal({ open, onClose, onSubmit, productos }) {
  const [motivo, setMotivo] = useState('');
  const [ordenCompra, setOrdenCompra] = useState(null);
  const [entradaItems, setEntradaItems] = useState([]);
  const [comentario, setComentario] = useState('');
  const [errors, setErrors] = useState({});
  const [openOrdenesModal, setOpenOrdenesModal] = useState(false);

  useEffect(() => {
    if (motivo === 'orden de compra' && ordenCompra) {
      // Cargar la OC seleccionada y filtrar ítems con cantidad pendiente
      axiosInstance
        .get(`ordenes/ordenes/${ordenCompra.id}/`)
        .then((res) => {
          const details = res.data.detalles || [];
          // Filtrar ítems que tengan cantidad pendiente mayor a 0
          const filteredDetails = details.filter(detail => detail.cantidad_pendiente > 0);
          const items = filteredDetails.map((detail) => {
            const prod = productos.find(
              (p) =>
                p.codigo.toLowerCase().trim() === detail.detalle.toLowerCase().trim() ||
                (p.nombre && p.nombre.toLowerCase().trim() === detail.detalle.toLowerCase().trim())
            );
            return {
              producto: prod || null,
              cantidad: detail.cantidad_pendiente, // Usamos la cantidad pendiente
              costo_unitario: detail.precio_unitario,
              editingPrecio: false,
              arrived: false,
              actualizar_precio: false,
            };
          });
          setEntradaItems(items);
        })
        .catch((err) => console.error("Error al cargar detalles de OC:", err));
    } else if (motivo !== 'orden de compra') {
      setEntradaItems([{ producto: null, cantidad: '', costo_unitario: '', editingPrecio: false, actualizar_precio: false }]);
      setOrdenCompra(null);
    }
  }, [motivo, ordenCompra, productos]);

  const handleAddItem = () => {
    setEntradaItems([
      ...entradaItems,
      { producto: null, cantidad: '', costo_unitario: '', editingPrecio: false, actualizar_precio: false },
    ]);
  };

  const handleRemoveItem = (index) => {
    const newItems = [...entradaItems];
    newItems.splice(index, 1);
    setEntradaItems(newItems);
  };

  const toggleArrived = (index) => {
    const newItems = [...entradaItems];
    newItems[index].arrived = !newItems[index].arrived;
    if (!newItems[index].arrived) {
      newItems[index].cantidad = '0';
    }
    setEntradaItems(newItems);
  };

  const handleSubmit = () => {
    const payload = {
      items: entradaItems.map((item) => ({
        producto: item.producto ? item.producto.id : null,
        cantidad: item.arrived ? parseInt(item.cantidad, 10) : 0,
        costo_unitario: item.editingPrecio
          ? parseFloat(item.costo_unitario)
          : item.producto
          ? parseFloat(item.producto.precio_compra)
          : null,
        actualizar_precio: item.actualizar_precio || false,
      })),
      motivo: motivo === 'orden de compra' ? 'recepcion_oc' : motivo,
      orden_compra: motivo === 'orden de compra' && ordenCompra ? ordenCompra.id : null,
      comentario,
    };
    onSubmit(payload);
    setMotivo('');
    setOrdenCompra(null);
    setEntradaItems([]);
    setComentario('');
    setErrors({});
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="md">
      <DialogTitle>Registrar Entrada</DialogTitle>
      <DialogContent>
        <Box sx={{ mt: 2 }}>
          <FormControl fullWidth variant="standard">
            <InputLabel>Motivo</InputLabel>
            <Select
              value={motivo}
              onChange={(e) => setMotivo(e.target.value)}
              label="Motivo"
            >
              <MenuItem value="compra">Compra</MenuItem>
              <MenuItem value="devolucion">Devolución</MenuItem>
              <MenuItem value="orden de compra">Orden de Compra</MenuItem>
            </Select>
          </FormControl>
        </Box>
        {motivo === 'orden de compra' && (
          <Box sx={{ mt: 2 }}>
            <Button variant="outlined" onClick={() => setOpenOrdenesModal(true)}>
              Seleccionar OC Pendiente
            </Button>
            {ordenCompra && (
              <Typography variant="body2" sx={{ mt: 1 }}>
                OC Seleccionada: {ordenCompra.numero_orden} - {ordenCompra.empresa}
              </Typography>
            )}
          </Box>
        )}
        {motivo === 'orden de compra' && entradaItems.length > 0 && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6">Confirmar Ítems Pendientes de la OC</Typography>
            {entradaItems.map((item, index) => (
              <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 2, mt: 1 }}>
                <Typography sx={{ minWidth: 180 }}>
                  {item.producto ? `${item.producto.codigo} - ${item.producto.nombre}` : "Producto no seleccionado"}
                </Typography>
                <TextField
                  label="Cantidad Pendiente"
                  type="number"
                  variant="standard"
                  value={item.cantidad}
                  onChange={(e) => {
                    const newItems = [...entradaItems];
                    newItems[index].cantidad = e.target.value;
                    setEntradaItems(newItems);
                  }}
                />
                <TextField
                  label="Costo Unitario"
                  type="number"
                  variant="standard"
                  value={item.costo_unitario}
                  onChange={(e) => {
                    const newItems = [...entradaItems];
                    newItems[index].costo_unitario = e.target.value;
                    setEntradaItems(newItems);
                  }}
                />
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={item.arrived || false}
                      onChange={() => toggleArrived(index)}
                    />
                  }
                  label="Llegó"
                />
              </Box>
            ))}
          </Box>
        )}
        {motivo !== 'orden de compra' && (
          <>
            {entradaItems.map((item, index) => (
              <Box key={index} sx={{ display: 'flex', gap: 2, mt: 2, alignItems: 'center' }}>
                <Autocomplete
                  freeSolo
                  options={productos || []}
                  getOptionLabel={(option) =>
                    typeof option === 'string' ? option : `${option.codigo} - ${option.nombre}`
                  }
                  value={item.producto}
                  onChange={(event, newValue) => {
                    const newItems = [...entradaItems];
                    newItems[index].producto = newValue;
                    setEntradaItems(newItems);
                  }}
                  renderInput={(params) => (
                    <TextField {...params} label="Producto" variant="standard" />
                  )}
                  fullWidth
                />
                <TextField
                  label="Cantidad Recibida"
                  type="number"
                  variant="standard"
                  value={item.cantidad}
                  onChange={(e) => {
                    const newItems = [...entradaItems];
                    newItems[index].cantidad = e.target.value;
                    setEntradaItems(newItems);
                  }}
                />
                <TextField
                  label="Costo Unitario"
                  type="number"
                  variant="standard"
                  value={item.costo_unitario}
                  onChange={(e) => {
                    const newItems = [...entradaItems];
                    newItems[index].costo_unitario = e.target.value;
                    setEntradaItems(newItems);
                  }}
                  disabled={!item.editingPrecio}
                />
                <Button
                  variant="outlined"
                  onClick={() => {
                    const newItems = [...entradaItems];
                    newItems[index].editingPrecio = !newItems[index].editingPrecio;
                    setEntradaItems(newItems);
                  }}
                >
                  {item.editingPrecio ? 'Usar Precio Predefinido' : 'Cambiar Precio'}
                </Button>
                <Button variant="outlined" color="error" onClick={() => handleRemoveItem(index)}>
                  Eliminar
                </Button>
              </Box>
            ))}
            <Box sx={{ mt: 2 }}>
              <Button variant="outlined" onClick={handleAddItem}>
                Agregar Ítem
              </Button>
            </Box>
          </>
        )}
        <Box sx={{ mt: 2 }}>
          <TextField
            label="Comentario"
            fullWidth
            variant="standard"
            multiline
            rows={3}
            value={comentario}
            onChange={(e) => setComentario(e.target.value)}
          />
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancelar</Button>
        <Button onClick={handleSubmit} variant="contained">
          Registrar Entrada
        </Button>
      </DialogActions>
      <OrdenesModal
        open={openOrdenesModal}
        onClose={() => setOpenOrdenesModal(false)}
        onSelect={(order) => {
          setOrdenCompra(order);
          setOpenOrdenesModal(false);
        }}
      />
    </Dialog>
  );
}

export default EntradaModal;
