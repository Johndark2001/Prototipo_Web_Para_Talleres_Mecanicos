export default function PantallaCarga() {
  return (
    <div className="flex min-h-dvh items-center justify-center" aria-busy="true">
      <span
        className="size-8 animate-spin rounded-full border-4 border-primario border-t-transparent"
        aria-hidden="true"
      />
      <span className="sr-only">Cargando…</span>
    </div>
  )
}
