// src/pages/InventarioPage.jsx
import React, { useEffect, useState } from 'react';
import axiosInstance from '../api/axiosInstance';
import {
  Container,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  Button,
  Box,
  TablePagination,
  TextField,
  FormControlLabel,
  Checkbox,
  Snackbar,
  Alert
} from '@mui/material';
import EntradaModal from '../components/EntradaModal';
import SalidaModal from '../components/SalidaModal';
import NuevoProductoModal from '../components/NuevoProductoModal';

function InventarioPage() {
  const [productos, setProductos] = useState([]);
  const [ordenes, setOrdenes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);

  // Estados para modales
  const [openEntrada, setOpenEntrada] = useState(false);
  const [openSalida, setOpenSalida] = useState(false);
  const [openNuevoProducto, setOpenNuevoProducto] = useState(false);

  // Estados para búsqueda y filtro
  const [searchTerm, setSearchTerm] = useState('');
  const [filterUnderMin, setFilterUnderMin] = useState(false);

  // Estado para feedback al usuario
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState('success'); // success, error, warning, info

  useEffect(() => {
    fetchProductos();
    fetchOrdenes();
  }, []);

  const fetchProductos = async () => {
    try {
      const response = await axiosInstance.get('productos/');
      setProductos(response.data);
    } catch (error) {
      console.error('Error al cargar productos:', error);
      showSnackbar("Error al cargar productos", "error");
    } finally {
      setLoading(false);
    }
  };

  const fetchOrdenes = async () => {
    try {
      const response = await axiosInstance.get('ordenes/');
      setOrdenes(response.data);
    } catch (error) {
      console.error('Error al cargar órdenes:', error);
      showSnackbar("Error al cargar órdenes", "error");
    }
  };

  const valorTotalBodega = productos.reduce(
    (acc, producto) => acc + producto.stock_actual * producto.precio_compra,
    0
  );

  // Filtrar productos basados en el término de búsqueda y el filtro de stock mínimo
  const filteredProducts = productos.filter((producto) => {
    const term = searchTerm.toLowerCase();
    const match =
      producto.nombre.toLowerCase().includes(term) ||
      producto.codigo.toLowerCase().includes(term) ||
      producto.ubicacion.toLowerCase().includes(term) ||
      String(producto.consignacion).toLowerCase().includes(term);
    const underMin = filterUnderMin ? producto.stock_actual < producto.stock_minimo : true;
    return match && underMin;
  });

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const showSnackbar = (message, severity = "success") => {
    setSnackbarMessage(message);
    setSnackbarSeverity(severity);
    setSnackbarOpen(true);
  };

  const handleRegistrarEntrada = async (payload) => {
    try {
      await axiosInstance.post('movimientos/entradas/', payload);
      showSnackbar("Entrada registrada exitosamente", "success");
      fetchProductos();
    } catch (error) {
      console.error('Error al registrar entrada:', error);
      showSnackbar("Error al registrar entrada", "error");
    }
  };

  const handleRegistrarSalida = async (payload) => {
    try {
      await axiosInstance.post('movimientos/salidas/', payload);
      showSnackbar("Salida registrada exitosamente", "success");
      fetchProductos();
    } catch (error) {
      console.error('Error al registrar salida:', error);
      showSnackbar("Error al registrar salida", "error");
    }
  };

  const handleCrearProducto = async (payload) => {
    try {
      await axiosInstance.post('productos/', payload);
      showSnackbar("Producto creado exitosamente", "success");
      fetchProductos();
    } catch (error) {
      console.error('Error al crear producto:', error);
      showSnackbar("Error al crear producto", "error");
    }
  };

  if (loading) {
    return (
      <Container sx={{ textAlign: 'center', marginTop: '2rem' }}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container>
      {/* Encabezado */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', my: 2 }}>
        <Typography variant="h5">Inventario de Productos</Typography>
        <Typography variant="h6" color="primary">
          Valor Total: ${valorTotalBodega.toFixed(2)}
        </Typography>
      </Box>
      
      {/* Barra de búsqueda y filtro */}
      <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 2 }}>
        <TextField
          label="Buscar (nombre, código, ubicación, consignación, descripción)"
          variant="outlined"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          fullWidth
        />
        <FormControlLabel
          control={
            <Checkbox
              checked={filterUnderMin}
              onChange={(e) => setFilterUnderMin(e.target.checked)}
            />
          }
          label="Bajo stock mínimo"
        />
      </Box>

      {/* Botones de acción */}
      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
        <Button variant="contained" color="primary" onClick={() => setOpenEntrada(true)}>
          Registrar Entrada
        </Button>
        <Button variant="contained" color="primary" onClick={() => setOpenSalida(true)}>
          Registrar Salida
        </Button>
        <Button variant="outlined" color="secondary" onClick={() => setOpenNuevoProducto(true)}>
          Nuevo Producto
        </Button>
      </Box>

      {/* Tabla de inventario con paginación */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead sx={{ backgroundColor: 'red' }}>
            <TableRow>
              <TableCell sx={{ color: 'white' }}>Código</TableCell>
              <TableCell sx={{ color: 'white' }}>Nombre</TableCell>
              <TableCell sx={{ color: 'white' }}>Descripción</TableCell>
              <TableCell sx={{ color: 'white' }}>Stock Actual</TableCell>
              <TableCell sx={{ color: 'white' }}>Stock Mínimo</TableCell>
              <TableCell sx={{ color: 'white' }}>Precio Compra</TableCell>
              <TableCell sx={{ color: 'white' }}>Valor Total</TableCell>
              <TableCell sx={{ color: 'white' }}>Ubicación</TableCell>
              <TableCell sx={{ color: 'white' }}>Consignación</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredProducts
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((producto) => (
                <TableRow key={producto.id}>
                  <TableCell>{producto.codigo}</TableCell>
                  <TableCell>{producto.nombre}</TableCell>
                  <TableCell>{producto.descripcion}</TableCell>
                  <TableCell>{producto.stock_actual}</TableCell>
                  <TableCell>{producto.stock_minimo}</TableCell>
                  <TableCell>{producto.precio_compra}</TableCell>
                  <TableCell>{(producto.stock_actual * producto.precio_compra).toFixed(2)}</TableCell>
                  <TableCell>{producto.ubicacion}</TableCell>
                  <TableCell>{producto.consignacion ? producto.nombre_consignacion : 'n/a'}</TableCell>
                </TableRow>
              ))}
          </TableBody>
        </Table>
        <TablePagination
          component="div"
          count={filteredProducts.length}
          page={page}
          onPageChange={handleChangePage}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          rowsPerPageOptions={[5, 10, 25]}
        />
      </TableContainer>

      <EntradaModal
        open={openEntrada}
        onClose={() => setOpenEntrada(false)}
        onSubmit={handleRegistrarEntrada}
        productos={productos}
      />
      <SalidaModal
        open={openSalida}
        onClose={() => setOpenSalida(false)}
        onSubmit={handleRegistrarSalida}
        productos={productos}
      />
      <NuevoProductoModal
        open={openNuevoProducto}
        onClose={() => setOpenNuevoProducto(false)}
        onSubmit={handleCrearProducto}
      />

      <Snackbar
        open={snackbarOpen}
        autoHideDuration={4000}
        onClose={() => setSnackbarOpen(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={() => setSnackbarOpen(false)} severity={snackbarSeverity} sx={{ width: '100%' }}>
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </Container>
  );
}

export default InventarioPage;
