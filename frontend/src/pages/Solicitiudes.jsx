// src/pages/Solicitudes.jsx
import React, { useState, useEffect, useCallback } from 'react';
import {
  Container,
  Typography,
  Box,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TablePagination,
  Button,
  TextField
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import axiosInstance from '../api/axiosInstance';
import NuevaSolicitudModal from '../components/NuevaSolicitudModal';
import SolicitudDetalleModal from '../components/SolicitudDetalleModal';
import RefreshIcon from '@mui/icons-material/Refresh';
import { IconButton } from '@mui/material';

function Solicitudes() {
  const [solicitudes, setSolicitudes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openNuevaSolicitud, setOpenNuevaSolicitud] = useState(false);
  const [detalleSolicitud, setDetalleSolicitud] = useState(null);
  const [openDetalle, setOpenDetalle] = useState(false);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  // Estados para búsqueda: searchInput y searchTerm para activar la búsqueda solo al confirmar
  const [searchInput, setSearchInput] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [fechaFiltro, setFechaFiltro] = useState(null);

  const fetchSolicitudes = useCallback(async () => {
    setLoading(true);
    try {
      let url = 'solicitudes/';
      // Si el backend no filtra por fecha, se hará el filtrado en el front-end
      if (searchTerm) {
        url += `?search=${encodeURIComponent(searchTerm)}`;
      }
      const response = await axiosInstance.get(url);
      setSolicitudes(response.data);
    } catch (error) {
      console.error('Error al cargar solicitudes:', error);
    } finally {
      setLoading(false);
    }
  }, [searchTerm]);

  useEffect(() => {
    fetchSolicitudes();
  }, [fetchSolicitudes]);

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  // Actualiza searchInput sin activar la búsqueda
  const handleSearchChange = (e) => {
    setSearchInput(e.target.value);
  };

  // Al presionar Enter o hacer clic en el botón, se actualiza searchTerm
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

  const handleNuevaSolicitud = async (payload) => {
    try {
      await axiosInstance.post('solicitudes/', payload);
      setOpenNuevaSolicitud(false);
      fetchSolicitudes();
    } catch (error) {
      console.error('Error al crear solicitud:', error);
    }
  };

  const handleVerDetalle = async (solicitud) => {
    try {
      const response = await axiosInstance.get(`solicitudes/${solicitud.id}/`);
      setDetalleSolicitud(response.data);
      setOpenDetalle(true);
    } catch (error) {
      console.error("Error al obtener detalle de la solicitud:", error);
    }
  };

  const handleDescargarPDF = (solicitudId) => {
    const url = `https://soldega-prod.rj.r.appspot.com/api/solicitudes/reporte/generar_pdf/?solicitud_id=${solicitudId}`;
    window.open(url, '_blank');
  };

  // Acciones de aprobación/rechazo para supervisores
  const handleAprobar = async (solicitudId) => {
    try {
      await axiosInstance.patch(`solicitudes/${solicitudId}/aprobar/`);
      fetchSolicitudes();
    } catch (error) {
      console.error('Error al aprobar la solicitud:', error);
    }
  };

  const handleRechazar = async (solicitudId) => {
    try {
      await axiosInstance.patch(`solicitudes/${solicitudId}/rechazar/`);
      fetchSolicitudes();
    } catch (error) {
      console.error('Error al rechazar la solicitud:', error);
    }
  };

  // Filtrado local: combina búsqueda por término y filtro por fecha (comparando la parte YYYY-MM-DD de fecha_creacion)
  const solicitudesFiltradas = solicitudes.filter((solicitud) => {
    const term = searchTerm.toLowerCase();
    const matchSearch =
      solicitud.numero_solicitud.toLowerCase().includes(term) ||
      solicitud.nombre_solicitante.toLowerCase().includes(term) ||
      solicitud.estado.toLowerCase().includes(term);
    let matchDate = true;
    if (fechaFiltro) {
      const selectedDate = fechaFiltro.toISOString().split('T')[0];
      const solDate = new Date(solicitud.fecha_creacion).toISOString().split('T')[0];
      matchDate = selectedDate === solDate;
    }
    return matchSearch && matchDate;
  });

  if (loading) {
    return (
      <Container sx={{ textAlign: 'center', marginTop: '2rem' }}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container>
 <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', my: 2 }}>
  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
    <Typography variant="h5">Solicitudes de Compra</Typography>
    <IconButton size="small" onClick={() => window.location.reload()}>
      <RefreshIcon />
    </IconButton>
  </Box>
  <Button variant="contained" color="primary" onClick={() => setOpenNuevaSolicitud(true)}>
    Nueva Solicitud
  </Button>
</Box>
      
      {/* Barra de búsqueda y filtro */}
      <Box sx={{ display: 'flex', gap: 2, mb: 2, alignItems: 'center' }}>
        <TextField
          label="Buscar (N° Solicitud, Solicitante, Estado)"
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
          label="Filtrar por Fecha"
          value={fechaFiltro}
          onChange={handleFechaChange}
          renderInput={(params) => <TextField {...params} sx={{ width: 200 }} />}
        />
      </Box>
      
      {/* Tabla de Solicitudes */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead sx={{ backgroundColor: 'red' }}>
            <TableRow>
              <TableCell sx={{ color: 'white' }}>N° Solicitud</TableCell>
              <TableCell sx={{ color: 'white' }}>Solicitante</TableCell>
              <TableCell sx={{ color: 'white' }}>Fecha</TableCell>
              <TableCell sx={{ color: 'white' }}>Estado</TableCell>
              <TableCell sx={{ color: 'white' }}>Acciones</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {solicitudesFiltradas
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((solicitud) => (
                <TableRow key={solicitud.id}>
                  <TableCell>{solicitud.numero_solicitud}</TableCell>
                  <TableCell>{solicitud.nombre_solicitante}</TableCell>
                  <TableCell>{new Date(solicitud.fecha_creacion).toLocaleDateString()}</TableCell>
                  <TableCell>{solicitud.estado}</TableCell>
                  <TableCell>
                    <Button variant="outlined" onClick={() => handleVerDetalle(solicitud)} sx={{ mr: 1 }}>
                      Ver Detalle
                    </Button>
                    <Button variant="contained" color="primary" onClick={() => handleDescargarPDF(solicitud.id)} sx={{ mr: 1 }}>
                      Descargar PDF
                    </Button>
                    <Button variant="contained" color="success" onClick={() => handleAprobar(solicitud.id)} sx={{ mr: 1 }}>
                      Aprobar
                    </Button>
                    <Button variant="contained" color="error" onClick={() => handleRechazar(solicitud.id)}>
                      Rechazar
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
          </TableBody>
        </Table>
        <TablePagination
          component="div"
          count={solicitudesFiltradas.length}
          page={page}
          onPageChange={handleChangePage}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          rowsPerPageOptions={[5, 10, 25]}
        />
      </TableContainer>

      {openNuevaSolicitud && (
        <NuevaSolicitudModal
          open={openNuevaSolicitud}
          onClose={() => setOpenNuevaSolicitud(false)}
          onSubmit={handleNuevaSolicitud}
        />
      )}

      {detalleSolicitud && (
        <SolicitudDetalleModal
          open={openDetalle}
          onClose={() => setOpenDetalle(false)}
          solicitud={detalleSolicitud}
        />
      )}
    </Container>
  );
}

export default Solicitudes;
