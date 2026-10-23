import { BrowserRouter, Route, Routes } from 'react-router'

import Layout from './components/Layout.jsx'
import { ROLES } from './constantes.js'
import Dashboard from './pages/Dashboard.jsx'
import Login from './pages/Login.jsx'
import NoEncontrada from './pages/NoEncontrada.jsx'
import Usuarios from './pages/Usuarios.jsx'
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
