// src/pages/AlertasPage.jsx
import React, { useState, useEffect, useContext } from 'react';
import {
  Container,
  Typography,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  TextField,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import axiosInstance from '../api/axiosInstance';
import { AuthContext } from '../contexts/AuthContext';

function AlertasPage() {
  const { user } = useContext(AuthContext);
  const [alertas, setAlertas] = useState([]);
  const [loading, setLoading] = useState(false);
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);
  const [filterEstado, setFilterEstado] = useState("todos");

  const fetchAlertas = async () => {
    setLoading(true);
    try {
      let url = 'alertas/';
      const params = [];
      if (startDate) params.push(`start_date=${startDate.format('YYYY-MM-DD')}`);
      if (endDate) params.push(`end_date=${endDate.format('YYYY-MM-DD')}`);
      if (params.length) url += '?' + params.join('&');
      const response = await axiosInstance.get(url);
      // Ordenar alertas por fecha_creacion descendente
      const sortedAlertas = response.data.sort(
        (a, b) => new Date(b.fecha_creacion) - new Date(a.fecha_creacion)
      );
      setAlertas(sortedAlertas);
    } catch (error) {
      console.error("Error al cargar alertas:", error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchAlertas();
  }, [startDate, endDate]);

  const resolverAlerta = async (alertaId, nuevoEstado) => {
    try {
      const response = await axiosInstance.patch(`alertas/${alertaId}/resolver/`, {
        estado: nuevoEstado,
        comentario: `Resuelta por ${user.username}`,
      });
      setAlertas(alertas.map(a => (a.id === alertaId ? response.data : a)));
    } catch (error) {
      console.error("Error al resolver alerta:", error);
    }
  };

  // Filtrar alertas según el estado seleccionado
  const filteredAlertas =
    filterEstado === "todos"
      ? alertas
      : alertas.filter((alerta) => alerta.estado === filterEstado);

  return (
    <Container>
      <Typography variant="h5" gutterBottom>
        Alertas
      </Typography>
      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
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
        <FormControl variant="standard" sx={{ minWidth: 150 }}>
          <InputLabel id="estado-alerta-label">Estado</InputLabel>
          <Select
            labelId="estado-alerta-label"
            value={filterEstado}
            onChange={(e) => setFilterEstado(e.target.value)}
            label="Estado"
          >
            <MenuItem value="todos">Todos</MenuItem>
            <MenuItem value="pendiente">Pendiente</MenuItem>
            <MenuItem value="resuelta">Resuelta</MenuItem>
            <MenuItem value="rechazada">Rechazada</MenuItem>
          </Select>
        </FormControl>
        <Button variant="contained" onClick={fetchAlertas}>
          Filtrar
        </Button>
      </Box>
      {loading ? (
        <Box sx={{ textAlign: 'center', mt: 2 }}>
          <CircularProgress />
        </Box>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Fecha Creación</TableCell>
                <TableCell>Tipo</TableCell>
                <TableCell>Estado</TableCell>
                <TableCell>Fecha Resolución</TableCell>
                <TableCell>Mensaje</TableCell>
                <TableCell>Acciones</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredAlertas.map((alerta) => (
                <TableRow key={alerta.id}>
                  <TableCell>
                    {new Date(alerta.fecha_creacion).toLocaleString()}
                  </TableCell>
                  <TableCell>{alerta.tipo}</TableCell>
                  <TableCell>{alerta.estado}</TableCell>
                  <TableCell>
                    {alerta.fecha_resolucion
                      ? new Date(alerta.fecha_resolucion).toLocaleString()
                      : '-'}
                  </TableCell>
                  <TableCell>{alerta.mensaje}</TableCell>
                  <TableCell>
                    {alerta.estado === 'pendiente' && (
                      <>
                        {alerta.tipo === 'salida_alta' ? (
                          user.rol === 'supervisor' && (
                            <>
                              <Button
                                variant="contained"
                                color="primary"
                                onClick={() => resolverAlerta(alerta.id, 'resuelta')}
                              >
                                Aprobar
                              </Button>
                              <Button
                                variant="outlined"
                                color="error"
                                onClick={() => resolverAlerta(alerta.id, 'rechazada')}
                                sx={{ ml: 1 }}
                              >
                                Rechazar
                              </Button>
                            </>
                          )
                        ) : (
                          (user.rol === 'tecnico' ||
                            user.rol === 'supervisor' ||
                            user.rol === 'secretario tecnico') && (
                            <>
                              <Button
                                variant="contained"
                                color="primary"
                                onClick={() => resolverAlerta(alerta.id, 'resuelta')}
                              >
                                Resuelta
                              </Button>
                              <Button
                                variant="outlined"
                                color="error"
                                onClick={() => resolverAlerta(alerta.id, 'rechazada')}
                                sx={{ ml: 1 }}
                              >
                                Rechazar
                              </Button>
                            </>
                          )
                        )}
                      </>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Container>
  );
}

export default AlertasPage;
