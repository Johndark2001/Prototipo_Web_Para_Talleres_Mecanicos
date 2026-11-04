// Ilustración de línea del taller: un carro en la rampa, dos engranajes que encajan, una
// llave, un repuesto (bujía) y la curva de un escáner de diagnóstico. Es decorativa
// (aria-hidden) y usa currentColor, así sirve sobre fondo oscuro o claro.
// Los engranajes giran muy despacio; animado={false} los detiene (pantallas de uso diario)
// y con "menos movimiento" quedan quietos (index.css).
function Engranaje({ cx, cy, r, dientes, grosor, girar = false, inverso = false }) {
  const paso = (2 * Math.PI * r) / dientes
  return (
    <g
      className={girar ? 'animate-girar-lento' : undefined}
      style={{
        transformBox: 'fill-box',
        transformOrigin: 'center',
        animationDirection: inverso ? 'reverse' : undefined,
      }}
    >
      <circle
        cx={cx}
        cy={cy}
        r={r}
        strokeWidth={grosor}
        strokeDasharray={`${paso / 2} ${paso / 2}`}
        strokeLinecap="butt"
      />
      <circle cx={cx} cy={cy} r={r - grosor * 0.9} strokeWidth="2" />
      <circle cx={cx} cy={cy} r={r * 0.28} strokeWidth="2" />
    </g>
  )
}

export default function IlustracionTaller({ className = '', animado = true }) {
  return (
    <svg
      viewBox="0 0 400 260"
      fill="none"
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      {/* Curva del escáner de diagnóstico */}
      <path
        d="M24 64h44l10-22 14 46 12-34 8 10h40"
        strokeWidth="2.5"
        className="opacity-70"
      />
      <circle cx="152" cy="64" r="3.5" fill="currentColor" className="opacity-70" />

      {/* Engranajes */}
      <g className="opacity-90">
        <Engranaje cx={318} cy={70} r={30} dientes={12} grosor={9} girar={animado} />
        <Engranaje cx={262} cy={38} r={17} dientes={8} grosor={7} girar={animado} inverso />
      </g>

      {/* Llave de boca: la abertura del anillo mira hacia afuera, el otro extremo es de estrella */}
      <g transform="translate(184 28) rotate(38)" className="opacity-70">
        <circle r="11" strokeWidth="5.5" strokeDasharray="51 18" transform="rotate(-137)" strokeLinecap="butt" />
        <path d="M11 0h40" strokeWidth="7" />
        <circle cx="57" r="6" strokeWidth="4" />
      </g>

      {/* Bujía (repuesto) */}
      <g strokeWidth="2.5" className="opacity-60">
        <path d="M58 118h16M60 118v14h12v-14M62 132v10h8v-10M66 142v10M63 104h6v14h-6z" />
      </g>

      {/* Carro */}
      <g strokeWidth="3">
        <path d="M48 204h34a26 26 0 0 1 52 0h128a26 26 0 0 1 52 0h36v-20c0-12-8-18-20-19l-42-6-32-27c-6-5-12-7-21-7h-86c-9 0-15 3-21 8l-32 27-34 4c-10 1-14 8-14 18z" />
        <path d="M140 158l20-20h44v20zM214 138h28c5 0 9 2 13 5l15 15h-56z" strokeWidth="2.5" />
        <circle cx="108" cy="206" r="19" />
        <circle cx="108" cy="206" r="7" />
        <circle cx="288" cy="206" r="19" />
        <circle cx="288" cy="206" r="7" />
        <path d="M340 178h8M52 182h8" strokeWidth="2.5" />
      </g>

      {/* Rampa del taller */}
      <path d="M20 236h360" strokeWidth="3" className="opacity-80" />
      <path d="M40 248h320" strokeWidth="2" strokeDasharray="10 12" className="opacity-40" />
    </svg>
  )
}
