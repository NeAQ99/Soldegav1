
import RefreshIcon from '@mui/icons-material/Refresh';
import { IconButton } from '@mui/material';
import React, { useState, useEffect, useCallback } from 'react';
import { 
  Container, 
  Typography, 
  Box, 
  CircularProgress, 
  Button, 
  TextField, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow, 
  Paper, 
  TablePagination,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import axiosInstance from '../api/axiosInstance';
import CrearOCModal from '../components/CrearOCModal';
import OrdenDetalleModal from '../components/OrdenDetalleModal';


function Ordenes() {
  const [ordenes, setOrdenes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchInput, setSearchInput] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [fechaFiltro, setFechaFiltro] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const [openCrearOC, setOpenCrearOC] = useState(false);
  const [openDetalle, setOpenDetalle] = useState(false);
  const [ordenDetalle, setOrdenDetalle] = useState(null);
  const [proveedores, setProveedores] = useState([]);
  const [productos, setProductos] = useState([]);

  // La actualización del estado se hace en el back-end, por lo que en el front solo mostramos la propiedad
  // No se permite cambiar manualmente el estado.
  const fetchOrdenes = useCallback(async () => {
    setLoading(true);
    try {
      let url = 'ordenes/ordenes/';
      const params = [];
      if (searchTerm) params.push(`search=${encodeURIComponent(searchTerm)}`);
      if (params.length > 0) url += '?' + params.join('&');
      const response = await axiosInstance.get(url);
      // Verificar si la respuesta está paginada
      const data = response.data.results ? response.data.results : response.data;
      setOrdenes(data);
    } catch (error) {
      console.error('Error al cargar órdenes:', error);
    } finally {
      setLoading(false);
    }
  }, [searchTerm]);
  

  const fetchProveedores = async () => {
    try {
      const response = await axiosInstance.get('ordenes/proveedores/');
      setProveedores(response.data);
    } catch (error) {
      console.error('Error al cargar proveedores:', error);
    }
  };

  const fetchProductos = async () => {
    try {
      const response = await axiosInstance.get('productos/');
      setProductos(response.data);
    } catch (error) {
      console.error('Error al cargar productos:', error);
    }
  };

  useEffect(() => {
    fetchProveedores();
    fetchProductos();
  }, []);

  const ordenesFiltradas = ordenes.filter((orden) => {
    const term = searchTerm.toLowerCase();
    const matchSearch =
      orden.numero_orden.toLowerCase().includes(term) ||
      (orden.usuario && orden.usuario.username.toLowerCase().includes(term)) ||
      orden.estado.toLowerCase().includes(term);
    
    let matchDate = true;
    if (fechaFiltro) {
      const selectedDate = fechaFiltro.toISOString().split('T')[0];
      const orderDate = new Date(orden.fecha).toISOString().split('T')[0];
      matchDate = selectedDate === orderDate;
    }
    return matchSearch && matchDate;
  });

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleSearchChange = (e) => {
    setSearchInput(e.target.value);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      setSearchTerm(searchInput);
      setPage(0);
    }
  };

  const handleFechaChange = (newDate) => {
    setFechaFiltro(newDate);
    setPage(0);
  };

  const handleCrearOrden = async (payload) => {
    try {
      await axiosInstance.post('ordenes/ordenes/', payload);
      setOpenCrearOC(false);
      fetchOrdenes();
    } catch (error) {
      console.error('Error al crear OC:', error);
    }
  };

  const handleMoreDetails = async (orden) => {
    try {
      const response = await axiosInstance.get(`ordenes/ordenes/${orden.id}/`);
      setOrdenDetalle(response.data);
      setOpenDetalle(true);
    } catch (error) {
      console.error("Error al obtener detalles de la orden:", error);
    }
  };

  const handleDownloadPDF = (ordenId) => {
    const url = `https://soldega-prod.rj.r.appspot.com/api/ordenes/reporte/generar_pdf/?orden_id=${ordenId}`;
    window.open(url, '_blank');
  };

  // Función para recargar datos sin recargar la página completa
  const handleRecargar = () => {
    fetchOrdenes();
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
      {/* Encabezado y botones */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', my: 2 }}>
        <Typography variant="h5">Órdenes de Compra</Typography>
        <Box>
          <Button variant="contained" color="primary" onClick={() => setOpenCrearOC(true)}>
            Nueva Orden de Compra
          </Button>
          <IconButton size="small" onClick={handleRecargar}>
            <RefreshIcon />
          </IconButton>
        </Box>
      </Box>
      
      {/* Barra de búsqueda y filtros */}
      <Box sx={{ display: 'flex', gap: 2, mb: 2, alignItems: 'center' }}>
        <TextField
          label="Buscar (N° Orden, Usuario, Estado)"
          variant="outlined"
          value={searchInput}
          onChange={handleSearchChange}
          onKeyPress={handleKeyPress}
          fullWidth
        />
        <Button 
          variant="contained" 
          onClick={() => {
            setSearchTerm(searchInput);
            setPage(0);
          }}
        >
          Buscar
        </Button>
        <DatePicker
          label="Fecha"
          value={fechaFiltro}
          onChange={handleFechaChange}
          renderInput={(params) => <TextField {...params} sx={{ width: 200 }} />}
        />
      </Box>
      
      {/* Tabla de Órdenes */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead sx={{ backgroundColor: 'red' }}>
            <TableRow>
              <TableCell sx={{ color: 'white' }}>N° Orden</TableCell>
              <TableCell sx={{ color: 'white' }}>Estado</TableCell>
              <TableCell sx={{ color: 'white' }}>Fecha</TableCell>
              <TableCell sx={{ color: 'white' }}>Usuario Creador</TableCell>
              <TableCell sx={{ color: 'white' }}>Acciones</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {ordenesFiltradas
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((orden) => (
                <TableRow key={orden.id}>
                  <TableCell>{orden.numero_orden}</TableCell>
                  <TableCell>{orden.estado}</TableCell>
                  <TableCell>{new Date(orden.fecha).toLocaleDateString()}</TableCell>
                  <TableCell>{orden.usuario ? orden.usuario.username : 'Desconocido'}</TableCell>
                  <TableCell>
                    <Button variant="outlined" onClick={() => handleMoreDetails(orden)} sx={{ mr: 1 }}>
                      Más Detalle
                    </Button>
                    <Button variant="contained" color="primary" onClick={() => handleDownloadPDF(orden.id)}>
                      Descargar PDF
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
          </TableBody>
        </Table>
        <TablePagination
          component="div"
          count={ordenesFiltradas.length}
          page={page}
          onPageChange={handleChangePage}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          rowsPerPageOptions={[5, 10, 25]}
        />
      </TableContainer>
      
      {/* Modal para crear nueva OC */}
      {openCrearOC && (
        <CrearOCModal
          open={openCrearOC}
          onClose={() => setOpenCrearOC(false)}
          onSubmit={handleCrearOrden}
          proveedores={proveedores}
          productos={productos}
        />
      )}
      
      {/* Modal para ver detalles de la orden */}
      {ordenDetalle && (
        <OrdenDetalleModal
          open={openDetalle}
          onClose={() => setOpenDetalle(false)}
          orden={ordenDetalle}
        />
      )}
    </Container>
  );
}

export default Ordenes;
