import { useEffect, useState } from 'react'

/** Devuelve `valor` cuando el usuario deja de escribir, para no consultar en cada tecla. */
export function useRetrasado(valor, milisegundos = 300) {
  const [retrasado, setRetrasado] = useState(valor)

  useEffect(() => {
    const temporizador = setTimeout(() => setRetrasado(valor), milisegundos)
    return () => clearTimeout(temporizador)
  }, [valor, milisegundos])

  return retrasado
}
