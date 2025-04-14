import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  TablePagination,
  Button,
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Switch,
  FormControlLabel
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import axiosInstance from '../api/axiosInstance';
import { PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';

function MovimientosPage() {
  const [tab, setTab] = useState(0); // 0: entradas, 1: salidas
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);
  const [entradas, setEntradas] = useState([]);
  const [salidas, setSalidas] = useState([]);
  const [totales, setTotales] = useState({ entradas: 0, salidas: 0 });
  const [loading, setLoading] = useState(true);
  
  // Estados para paginación
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);

  // Estado para almacenar la lista de productos (para lookup)
  const [productos, setProductos] = useState([]);

  // Estado para el toggle de consignación: false = Todos, true = Consignación
  const [filtrarConsignacion, setFiltrarConsignacion] = useState(false);

  // Estados para el modal de detalle
  const [openDetalle, setOpenDetalle] = useState(false);
  const [movimientoDetalle, setMovimientoDetalle] = useState(null);

  // Cargar productos para lookup
  useEffect(() => {
    const fetchProductos = async () => {
      try {
        const res = await axiosInstance.get('productos/');
        setProductos(res.data);
      } catch (error) {
        console.error("Error al cargar productos:", error);
      }
    };
    fetchProductos();
  }, []);
  
  const fetchMovimientos = async () => {
    let params = {};
    if (startDate && endDate) {
      params = {
        start_date: startDate.format('YYYY-MM-DD'),
        end_date: endDate.format('YYYY-MM-DD'),
      };
    }
    if (filtrarConsignacion) {
      params.consignacion = "true";
    }
    setLoading(true);
    try {
      const [resEntradas, resSalidas] = await Promise.all([
        axiosInstance.get('movimientos/entradas/', { params }),
        axiosInstance.get('movimientos/salidas/', { params }),
      ]);
      // Verifica si la respuesta tiene results, sino usa directamente los datos
      const entradasData = resEntradas.data.results ? resEntradas.data.results : resEntradas.data;
      const salidasData = resSalidas.data.results ? resSalidas.data.results : resSalidas.data;
      setEntradas(entradasData);
      setSalidas(salidasData);
      const totalEntradas = entradasData.reduce((acc, item) => acc + item.cantidad, 0);
      const totalSalidas = salidasData.reduce((acc, item) => acc + item.cantidad, 0);
      setTotales({ entradas: totalEntradas, salidas: totalSalidas });
    } catch (error) {
      console.error('Error al cargar movimientos:', error);
    } finally {
      setLoading(false);
    }
  };
  

  useEffect(() => {
    fetchMovimientos();
    // eslint-disable-next-line
  }, [startDate, endDate, filtrarConsignacion]);

  const dataPie = [
    { name: 'Entradas', value: totales.entradas },
    { name: 'Salidas', value: totales.salidas },
  ];
  const COLORS = ['#0088FE', '#FF8042'];

  const handleDownloadPDF = () => {
    const tipo = tab === 0 ? 'entrada' : 'salida';
    let url = `https://soldega-prod.rj.r.appspot.com/api/movimientos/reporte/generar_pdf/?tipo=${tipo}`;
    if (startDate && endDate) {
      url += `&start_date=${startDate.format('YYYY-MM-DD')}&end_date=${endDate.format('YYYY-MM-DD')}`;
    }
    if (filtrarConsignacion) {
      url += `&consignacion=true`;
    }
    window.open(url, '_blank');
  };

  // Función para obtener el código del producto. Si 'producto' es un objeto, lo usa; si es un ID, busca en la lista.
  const getProductoCodigo = (producto) => {
    if (producto && typeof producto === 'object' && producto.codigo) {
      return producto.codigo;
    } else if (producto) {
      // Buscamos el producto en el listado
      const prod = productos.find(p => String(p.id) === String(producto));
      return prod ? prod.codigo : '';
    }
    return '';
  };

  // Función para obtener el nombre del producto.
  const getProductoNombre = (producto) => {
    if (producto && typeof producto === 'object' && producto.nombre) {
      return producto.nombre;
    } else if (producto) {
      const prod = productos.find(p => String(p.id) === String(producto));
      return prod ? prod.nombre : producto;
    }
    return producto;
  };

  const handleVerDetalle = (movimiento) => {
    setMovimientoDetalle(movimiento);
    setOpenDetalle(true);
  };

  const handleTabChange = (newTab) => {
    setTab(newTab);
    setPage(0);
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
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
      <Typography variant="h5" gutterBottom>
        Movimientos
      </Typography>
      <Box sx={{ display: 'flex', gap: 2, mb: 2, alignItems: 'center' }}>
        <DatePicker
          label="Fecha Inicio"
          value={startDate}
          onChange={(newValue) => setStartDate(newValue)}
          renderInput={(params) => <TextField {...params} />}
        />
        <DatePicker
          label="Fecha Fin"
          value={endDate}
          onChange={(newValue) => setEndDate(newValue)}
          renderInput={(params) => <TextField {...params} />}
        />
        <FormControlLabel
          control={
            <Switch
              checked={filtrarConsignacion}
              onChange={(e) => setFiltrarConsignacion(e.target.checked)}
              name="filtrarConsignacion"
              color="primary"
            />
          }
          label={filtrarConsignacion ? "Consignación" : "Todos"}
        />
        <Button variant="contained" color="primary" onClick={fetchMovimientos}>
          Filtrar
        </Button>
        <Button variant="outlined" color="secondary" onClick={handleDownloadPDF}>
          Descargar PDF
        </Button>
      </Box>
      <Box sx={{ mb: 2 }}>
        <Button
          variant={tab === 0 ? 'contained' : 'outlined'}
          onClick={() => handleTabChange(0)}
          sx={{ mr: 1 }}
        >
          Entradas
        </Button>
        <Button
          variant={tab === 1 ? 'contained' : 'outlined'}
          onClick={() => handleTabChange(1)}
        >
          Salidas
        </Button>
      </Box>
      {tab === 0 && (
        <>
          <Typography variant="subtitle1">Total Entradas: {totales.entradas}</Typography>
          <Paper sx={{ mt: 1 }}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Código Producto</TableCell>
                  <TableCell>Nombre Producto</TableCell>
                  <TableCell>Cantidad</TableCell>
                  <TableCell>Motivo</TableCell>
                  <TableCell>Fecha</TableCell>
                  <TableCell>Acciones</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {entradas
                  .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                  .map((entrada) => (
                    <TableRow key={entrada.id}>
                      <TableCell>{getProductoCodigo(entrada.producto)}</TableCell>
                      <TableCell>{getProductoNombre(entrada.producto)}</TableCell>
                      <TableCell>{entrada.cantidad}</TableCell>
                      <TableCell>
                        {entrada.motivo === 'recepcion_oc' && entrada.orden_compra
                          ? `OC ${entrada.orden_compra}`
                          : entrada.motivo}
                      </TableCell>
                      <TableCell>{new Date(entrada.fecha).toLocaleDateString()}</TableCell>
                      <TableCell>
                        <Button variant="outlined" onClick={() => handleVerDetalle(entrada)}>
                          Ver Detalle
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
              </TableBody>
            </Table>
          </Paper>
        </>
      )}
      {tab === 1 && (
        <>
          <Typography variant="subtitle1">Total Salidas: {totales.salidas}</Typography>
          <Paper sx={{ mt: 1 }}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Código Producto</TableCell>
                  <TableCell>Nombre Producto</TableCell>
                  <TableCell>Cantidad</TableCell>
                  <TableCell>Cargo</TableCell>
                  <TableCell>Fecha</TableCell>
                  <TableCell>Acciones</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {salidas.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((salida) => (
                  <TableRow key={salida.id}>
                    <TableCell>{getProductoCodigo(salida.producto)}</TableCell>
                    <TableCell>{getProductoNombre(salida.producto)}</TableCell>
                    <TableCell>{salida.cantidad}</TableCell>
                    <TableCell>{salida.cargo}</TableCell>
                    <TableCell>{new Date(salida.fecha).toLocaleDateString()}</TableCell>
                    <TableCell>
                      <Button variant="outlined" onClick={() => handleVerDetalle(salida)}>
                        Ver Detalle
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Paper>
        </>
      )}
      <TablePagination
        component="div"
        count={tab === 0 ? entradas.length : salidas.length}
        page={page}
        onPageChange={handleChangePage}
        rowsPerPage={rowsPerPage}
        onRowsPerPageChange={handleChangeRowsPerPage}
        rowsPerPageOptions={[5, 10, 25]}
      />
      <Box sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
        <PieChart width={300} height={300}>
          <Pie data={dataPie} cx={150} cy={150} innerRadius={60} outerRadius={100} fill="#8884d8" dataKey="value">
            {dataPie.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </Box>

      {/* Modal de detalle */}
      <Dialog open={openDetalle} onClose={() => setOpenDetalle(false)} fullWidth maxWidth="sm">
        <DialogTitle>Detalle del Movimiento</DialogTitle>
        <DialogContent dividers>
          {movimientoDetalle && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle1">
                Código Producto: {getProductoCodigo(movimientoDetalle.producto)}
              </Typography>
              <Typography variant="subtitle1">
                Nombre Producto: {getProductoNombre(movimientoDetalle.producto)}
              </Typography>
              <Typography variant="subtitle1">
                Cantidad: {movimientoDetalle.cantidad}
              </Typography>
              <Typography variant="subtitle1">
                Tipo: {movimientoDetalle.motivo || movimientoDetalle.cargo}
              </Typography>
              <Typography variant="subtitle1">
                Fecha: {new Date(movimientoDetalle.fecha).toLocaleDateString()}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDetalle(false)} variant="contained">
            Cerrar
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}

export default MovimientosPage;
