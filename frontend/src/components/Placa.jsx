/** La placa se muestra como en el carro: amarilla, en mayúsculas y con letra monoespaciada. */
export default function Placa({ placa, grande = false }) {
  return (
    <span
      className={`inline-block shrink-0 rounded border-2 border-texto bg-placa font-mono font-bold tracking-wider text-texto ${
        grande ? 'px-3 py-1 text-xl' : 'px-1.5 py-0.5 text-sm'
      }`}
    >
      {placa}
    </span>
  )
}
