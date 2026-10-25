import { BrowserRouter, Route, Routes } from 'react-router'

import Layout from './components/Layout.jsx'
import { ROLES, ROLES_EDITAN_CLIENTES } from './constantes.js'
import ClienteDetalle from './pages/ClienteDetalle.jsx'
import ClienteFormulario from './pages/ClienteFormulario.jsx'
import Clientes from './pages/Clientes.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Login from './pages/Login.jsx'
import NoEncontrada from './pages/NoEncontrada.jsx'
import Usuarios from './pages/Usuarios.jsx'
import VehiculoDetalle from './pages/VehiculoDetalle.jsx'
import VehiculoFormulario from './pages/VehiculoFormulario.jsx'
import Vehiculos from './pages/Vehiculos.jsx'
import ProveedorSesion from './sesion/ProveedorSesion.jsx'
import RutaProtegida from './sesion/RutaProtegida.jsx'

export default function App() {
  return (
    <BrowserRouter>
      <ProveedorSesion>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            element={
              <RutaProtegida>
                <Layout />
              </RutaProtegida>
            }
          >
            <Route index element={<Dashboard />} />
            <Route path="clientes" element={<Clientes />} />
            <Route path="clientes/:id" element={<ClienteDetalle />} />
            <Route path="vehiculos" element={<Vehiculos />} />
            <Route path="vehiculos/:id" element={<VehiculoDetalle />} />
            {/* Crear y editar: solo ADMIN y RECEPCION; el mecánico solo consulta (SPEC §3). */}
            <Route element={<RutaProtegida roles={ROLES_EDITAN_CLIENTES} />}>
              <Route path="clientes/nuevo" element={<ClienteFormulario />} />
              <Route path="clientes/:id/editar" element={<ClienteFormulario />} />
              <Route path="vehiculos/nuevo" element={<VehiculoFormulario />} />
              <Route path="vehiculos/:id/editar" element={<VehiculoFormulario />} />
            </Route>
            <Route
              path="usuarios"
              element={
                <RutaProtegida roles={[ROLES.ADMIN]}>
                  <Usuarios />
                </RutaProtegida>
              }
            />
          </Route>
          <Route path="*" element={<NoEncontrada />} />
        </Routes>
      </ProveedorSesion>
    </BrowserRouter>
  )
}
