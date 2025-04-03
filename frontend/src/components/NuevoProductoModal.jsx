// src/components/NuevoProductoModal.jsx
import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  FormControlLabel,
  Checkbox,
} from '@mui/material';

function NuevoProductoModal({ open, onClose, onSubmit }) {
  const [productoData, setProductoData] = useState({
    codigo: '',
    nombre: '',
    descripcion: '',
    categoria: '',
    tipo: '',
    precio_compra: '',
    stock_actual: '',
    stock_minimo: '',
    consignacion: false,
    nombre_consignacion: '',
    ubicacion: '',
  });
  const [errors, setErrors] = useState({});

  const validateForm = () => {
    const formErrors = {};
    if (!productoData.codigo) {
      formErrors.codigo = 'El código es obligatorio (ej: P001)';
    }
    if (!productoData.nombre) {
      formErrors.nombre = 'El nombre es obligatorio';
    }
    if (
      !productoData.precio_compra ||
      parseFloat(productoData.precio_compra) <= 0
    ) {
      formErrors.precio_compra = 'El precio debe ser mayor a 0';
    }
    if (
      productoData.stock_actual === '' ||
      parseFloat(productoData.stock_actual) < 0
    ) {
      formErrors.stock_actual = 'El stock actual no puede ser negativo';
    }
    if (
      productoData.stock_minimo === '' ||
      parseFloat(productoData.stock_minimo) < 0
    ) {
      formErrors.stock_minimo = 'El stock mínimo no puede ser negativo';
    }
    if (!productoData.ubicacion) {
      formErrors.ubicacion =
        'La ubicación es obligatoria (ej: Pasillo 3, estante 2)';
    }
    return formErrors;
  };

  const handleSubmit = () => {
    const validationErrors = validateForm();
    setErrors(validationErrors);
    if (Object.keys(validationErrors).length === 0) {
      onSubmit(productoData);
      setProductoData({
        codigo: '',
        nombre: '',
        descripcion: '',
        categoria: '',
        tipo: '',
        precio_compra: '',
        stock_actual: '',
        stock_minimo: '',
        consignacion: false,
        nombre_consignacion: '',
        ubicacion: '',
      });
      setErrors({});
    }
  };

  useEffect(() => {
    if (open) setErrors({});
  }, [open]);

  return (
    <Dialog open={open} onClose={onClose} fullWidth>
      <DialogTitle>Nuevo Producto</DialogTitle>
      <DialogContent>
        <TextField
          autoFocus
          margin="dense"
          label="Código"
          fullWidth
          variant="standard"
          value={productoData.codigo}
          onChange={(e) =>
            setProductoData({ ...productoData, codigo: e.target.value })
          }
          error={Boolean(errors.codigo)}
          helperText={errors.codigo}
        />
        <TextField
          margin="dense"
          label="Nombre"
          fullWidth
          variant="standard"
          value={productoData.nombre}
          onChange={(e) =>
            setProductoData({ ...productoData, nombre: e.target.value })
          }
          error={Boolean(errors.nombre)}
          helperText={errors.nombre}
        />
        <TextField
          margin="dense"
          label="Descripción"
          fullWidth
          variant="standard"
          multiline
          rows={2}
          value={productoData.descripcion}
          onChange={(e) =>
            setProductoData({ ...productoData, descripcion: e.target.value })
          }
        />
        <TextField
          margin="dense"
          label="Categoría"
          fullWidth
          variant="standard"
          value={productoData.categoria}
          onChange={(e) =>
            setProductoData({ ...productoData, categoria: e.target.value })
          }
        />
        <TextField
          margin="dense"
          label="Tipo"
          fullWidth
          variant="standard"
          value={productoData.tipo}
          onChange={(e) =>
            setProductoData({ ...productoData, tipo: e.target.value })
          }
        />
        <TextField
          margin="dense"
          label="Precio Compra"
          fullWidth
          variant="standard"
          type="number"
          value={productoData.precio_compra}
          onChange={(e) =>
            setProductoData({ ...productoData, precio_compra: e.target.value })
          }
          error={Boolean(errors.precio_compra)}
          helperText={errors.precio_compra}
        />
        <TextField
          margin="dense"
          label="Stock Actual"
          fullWidth
          variant="standard"
          type="number"
          value={productoData.stock_actual}
          onChange={(e) =>
            setProductoData({ ...productoData, stock_actual: e.target.value })
          }
          error={Boolean(errors.stock_actual)}
          helperText={errors.stock_actual}
        />
        <TextField
          margin="dense"
          label="Stock Mínimo"
          fullWidth
          variant="standard"
          type="number"
          value={productoData.stock_minimo}
          onChange={(e) =>
            setProductoData({ ...productoData, stock_minimo: e.target.value })
          }
          error={Boolean(errors.stock_minimo)}
          helperText={errors.stock_minimo}
        />
        <Box sx={{ display: 'flex', alignItems: 'center', mt: 2 }}>
          <FormControlLabel
            control={
              <Checkbox
                checked={productoData.consignacion}
                onChange={(e) =>
                  setProductoData({
                    ...productoData,
                    consignacion: e.target.checked,
                  })
                }
              />
            }
            label="Consignación"
          />
          <TextField
            margin="dense"
            label="Nombre Consignación"
            fullWidth
            variant="standard"
            value={productoData.nombre_consignacion}
            onChange={(e) =>
              setProductoData({
                ...productoData,
                nombre_consignacion: e.target.value,
              })
            }
            disabled={!productoData.consignacion}
          />
        </Box>
        <TextField
          margin="dense"
          label="Ubicación"
          fullWidth
          variant="standard"
          value={productoData.ubicacion}
          onChange={(e) =>
            setProductoData({ ...productoData, ubicacion: e.target.value })
          }
          error={Boolean(errors.ubicacion)}
          helperText={errors.ubicacion}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancelar</Button>
        <Button onClick={handleSubmit}>Crear</Button>
      </DialogActions>
    </Dialog>
  );
}

export default NuevoProductoModal;
