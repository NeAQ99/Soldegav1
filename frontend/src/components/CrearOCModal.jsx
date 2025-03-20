// src/components/CrearOCModal.jsx
import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import Autocomplete from '@mui/material/Autocomplete';

function CrearOCModal({ open, onClose, onSubmit, proveedores, productos }) {
  // Datos generales de la OC
  const [empresa, setEmpresa] = useState('');
  const [nroCotizacion, setNroCotizacion] = useState('');
  const [mercaderiaPuestaEn, setMercaderiaPuestaEn] = useState('');
  const [proveedor, setProveedor] = useState(null);
  const [cargo, setCargo] = useState('');
  const [formaPago, setFormaPago] = useState('');
  const [plazoEntrega, setPlazoEntrega] = useState('');
  const [comentarios, setComentarios] = useState('');

  // Detalle de la orden: cada línea incluye producto (string u objeto), cantidad y precio unitario.
  const [detalleItems, setDetalleItems] = useState([
    { producto: '', cantidad: '', precio_unitario: '' },
  ]);

  const [errors, setErrors] = useState({});

  // Opciones para el dropdown de forma de pago
  const formaPagoOptions = [
    "30 días recepción de factura",
    "Transferencia electrónica",
    "Pago a 30-60-90 días",
    "Pago",
    "Pago a 30-60-90-120-150-180 días",
  ];

  const validateForm = () => {
    const errs = {};
    if (!empresa) {
      errs.empresa = 'El nombre de la empresa es obligatorio';
    }
    if (!nroCotizacion) {
      errs.nroCotizacion = 'El número de cotización es obligatorio';
    }
    if (!mercaderiaPuestaEn) {
      errs.mercaderiaPuestaEn = 'Debe ingresar la mercadería puesta en';
    }
    if (!proveedor) {
      errs.proveedor = 'Debe seleccionar un proveedor';
    }
    if (!cargo) {
      errs.cargo = 'El cargo es obligatorio';
    }
    if (!formaPago) {
      errs.formaPago = 'La forma de pago es obligatoria';
    }
    if (!plazoEntrega) {
      errs.plazoEntrega = 'El plazo de entrega es obligatorio';
    }
    const detalleErrors = detalleItems.map((item) => {
      const itemErr = {};
      if (!item.producto) {
        itemErr.producto = 'Ingrese o seleccione un producto';
      }
      if (!item.cantidad || parseInt(item.cantidad, 10) <= 0) {
        itemErr.cantidad = 'La cantidad debe ser mayor a 0';
      }
      if (!item.precio_unitario || parseFloat(item.precio_unitario) <= 0) {
        itemErr.precio_unitario = 'El precio debe ser mayor a 0';
      }
      return itemErr;
    });
    if (detalleErrors.some((err) => Object.keys(err).length > 0)) {
      errs.detalleItems = detalleErrors;
    }
    return errs;
  };

  const handleAddDetalleItem = () => {
    setDetalleItems([...detalleItems, { producto: '', cantidad: '', precio_unitario: '' }]);
  };

  const handleRemoveDetalleItem = (index) => {
    const newItems = [...detalleItems];
    newItems.splice(index, 1);
    setDetalleItems(newItems);
  };

  const handleSubmit = () => {
    const errs = validateForm();
    setErrors(errs);
    if (Object.keys(errs).length === 0) {
      // Armamos el payload: si el valor de producto es un objeto, se utiliza su nombre; de lo contrario, se toma la cadena ingresada.
      const payload = {
        empresa,
        nro_cotizacion: nroCotizacion,
        mercaderia_puesta_en: mercaderiaPuestaEn,
        proveedor_id: proveedor ? proveedor.id : null,
        cargo,
        forma_pago: formaPago,
        plazo_entrega: plazoEntrega,
        comentarios,
        detalles: detalleItems.map((item) => ({
          // Se usa el campo "detalle" para almacenar la información del producto; en este caso, el nombre
          detalle: typeof item.producto === 'object' ? item.producto.nombre : item.producto,
          cantidad: parseInt(item.cantidad, 10),
          precio_unitario: parseFloat(item.precio_unitario),
        })),
      };
      onSubmit(payload);
      // Resetear formulario
      setEmpresa('');
      setNroCotizacion('');
      setMercaderiaPuestaEn('');
      setProveedor(null);
      setCargo('');
      setFormaPago('');
      setPlazoEntrega('');
      setComentarios('');
      setDetalleItems([{ producto: '', cantidad: '', precio_unitario: '' }]);
      setErrors({});
    }
  };

  useEffect(() => {
    if (open) setErrors({});
  }, [open]);

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="md">
      <DialogTitle>Nueva Orden de Compra</DialogTitle>
      <DialogContent>
        {/* Datos generales */}
        <TextField
          autoFocus
          margin="dense"
          label="Empresa"
          fullWidth
          variant="standard"
          value={empresa}
          onChange={(e) => setEmpresa(e.target.value)}
          error={Boolean(errors.empresa)}
          helperText={errors.empresa}
        />
        <TextField
          margin="dense"
          label="N° Cotización"
          fullWidth
          variant="standard"
          value={nroCotizacion}
          onChange={(e) => setNroCotizacion(e.target.value)}
          error={Boolean(errors.nroCotizacion)}
          helperText={errors.nroCotizacion}
        />
        <TextField
          margin="dense"
          label="Mercadería puesta en"
          fullWidth
          variant="standard"
          value={mercaderiaPuestaEn}
          onChange={(e) => setMercaderiaPuestaEn(e.target.value)}
          error={Boolean(errors.mercaderiaPuestaEn)}
          helperText={errors.mercaderiaPuestaEn}
        />
        <Autocomplete
          options={proveedores || []}
          getOptionLabel={(option) => `${option.nombre_proveedor} (${option.rut})`}
          value={proveedor}
          onChange={(event, newValue) => setProveedor(newValue)}
          renderInput={(params) => (
            <TextField
              {...params}
              margin="dense"
              label="Proveedor"
              variant="standard"
              error={Boolean(errors.proveedor)}
              helperText={errors.proveedor}
            />
          )}
          fullWidth
          sx={{ mt: 2 }}
        />
        <TextField
          margin="dense"
          label="Cargo"
          fullWidth
          variant="standard"
          value={cargo}
          onChange={(e) => setCargo(e.target.value)}
          error={Boolean(errors.cargo)}
          helperText={errors.cargo || "Ej: maquinaria, taller, etc."}
        />
        <FormControl fullWidth margin="dense" variant="standard" error={Boolean(errors.formaPago)}>
          <InputLabel id="forma-pago-label">Forma de Pago</InputLabel>
          <Select
            labelId="forma-pago-label"
            value={formaPago}
            onChange={(e) => setFormaPago(e.target.value)}
            label="Forma de Pago"
          >
            {formaPagoOptions.map((option) => (
              <MenuItem key={option} value={option}>
                {option}
              </MenuItem>
            ))}
          </Select>
          {errors.formaPago && (
            <Typography variant="caption" color="error">
              {errors.formaPago}
            </Typography>
          )}
        </FormControl>
        <TextField
          margin="dense"
          label="Plazo de Entrega"
          fullWidth
          variant="standard"
          value={plazoEntrega}
          onChange={(e) => setPlazoEntrega(e.target.value)}
          error={Boolean(errors.plazoEntrega)}
          helperText={errors.plazoEntrega}
        />
        <TextField
          margin="dense"
          label="Comentarios"
          fullWidth
          variant="standard"
          multiline
          rows={3}
          value={comentarios}
          onChange={(e) => setComentarios(e.target.value)}
        />

        {/* Detalle de la Orden */}
        <Box sx={{ mt: 3 }}>
          <Typography variant="h6">Detalles de la Orden</Typography>
          {detalleItems.map((item, index) => (
            <Box key={index} sx={{ display: 'flex', gap: 2, mt: 2, alignItems: 'center' }}>
              <Autocomplete
                freeSolo
                options={productos || []}
                getOptionLabel={(option) =>
                  typeof option === 'string' ? option : `${option.codigo} - ${option.nombre}`
                }
                value={item.producto}
                onChange={(event, newValue) => {
                  const newItems = [...detalleItems];
                  newItems[index].producto = newValue;
                  setDetalleItems(newItems);
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Producto"
                    variant="standard"
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
                )}
                fullWidth
              />
              <TextField
                label="Cantidad"
                type="number"
                variant="standard"
                value={item.cantidad}
                onChange={(e) => {
                  const newItems = [...detalleItems];
                  newItems[index].cantidad = e.target.value;
                  setDetalleItems(newItems);
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
                label="Precio Unitario"
                type="number"
                variant="standard"
                value={item.precio_unitario}
                onChange={(e) => {
                  const newItems = [...detalleItems];
                  newItems[index].precio_unitario = e.target.value;
                  setDetalleItems(newItems);
                }}
                error={
                  errors.detalleItems &&
                  errors.detalleItems[index] &&
                  Boolean(errors.detalleItems[index].precio_unitario)
                }
                helperText={
                  errors.detalleItems &&
                  errors.detalleItems[index] &&
                  errors.detalleItems[index].precio_unitario
                }
              />
              <Button variant="outlined" color="error" onClick={() => handleRemoveDetalleItem(index)}>
                Eliminar
              </Button>
            </Box>
          ))}
          <Button variant="outlined" onClick={handleAddDetalleItem} sx={{ mt: 2 }}>
            Agregar Producto al Detalle
          </Button>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancelar</Button>
        <Button onClick={handleSubmit} variant="contained">
          Crear
        </Button>
      </DialogActions>

      {/* Aquí se integra el modal para seleccionar una OC pendiente */}
      {/* Si deseas que el modal de OC se abra solo cuando el motivo es "orden de compra", verifica que se llame aquí */}
      {/* Ejemplo: */}
      {/* <OrdenesModal
          open={openOrdenesModal}
          onClose={() => setOpenOrdenesModal(false)}
          onSelect={(order) => setOrdenCompra(order)}
      /> */}
    </Dialog>
  );
}

export default CrearOCModal;
