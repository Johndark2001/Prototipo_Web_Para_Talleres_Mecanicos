import { MarcaLogo } from './Logo.jsx'

export default function PantallaCarga() {
  return (
    <div className="flex min-h-dvh flex-col items-center justify-center gap-4" aria-busy="true">
      <MarcaLogo className="size-12" />
      <span
        className="size-6 animate-spin rounded-full border-[3px] border-primario border-t-transparent"
        aria-hidden="true"
      />
      <span className="sr-only">Cargando…</span>
    </div>
  )
}
