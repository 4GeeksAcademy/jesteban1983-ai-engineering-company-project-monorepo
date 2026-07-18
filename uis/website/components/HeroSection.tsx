interface HeroSectionProps {
  lowStockCount: number;
  inventoryValueUSD: number;
}

export function HeroSection({ lowStockCount, inventoryValueUSD }: HeroSectionProps) {
  return (
    <section className="rounded-3xl border border-slate-200 bg-gradient-to-r from-cyan-50 via-white to-emerald-50 px-6 py-12 shadow-sm md:px-10">
      <p className="inline-block rounded-full border border-cyan-200 bg-cyan-100 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-cyan-900">
        Logistica de ultima milla
      </p>
      <h1 className="mt-4 max-w-3xl text-4xl font-bold leading-tight text-slate-900 md:text-5xl">
        TrackFlow conecta inventario, envios y decisiones operativas en un mismo flujo.
      </h1>
      <p className="mt-4 max-w-2xl text-base text-slate-700 md:text-lg">
        Operamos en Mexico y Espana con reglas de negocio unificadas para reducir quiebres de stock,
        escoger mejores transportistas y mantener entregas a tiempo.
      </p>
      <div className="mt-8 grid gap-4 sm:grid-cols-2 md:grid-cols-3">
        <div className="rounded-2xl border border-white/70 bg-white p-4 shadow-sm">
          <p className="text-xs uppercase tracking-wide text-slate-500">Alertas de stock</p>
          <p className="mt-1 text-2xl font-semibold text-slate-900">{lowStockCount}</p>
        </div>
        <div className="rounded-2xl border border-white/70 bg-white p-4 shadow-sm">
          <p className="text-xs uppercase tracking-wide text-slate-500">Valor inventario</p>
          <p className="mt-1 text-2xl font-semibold text-slate-900">${inventoryValueUSD.toLocaleString()}</p>
        </div>
        <div className="rounded-2xl border border-white/70 bg-white p-4 shadow-sm">
          <p className="text-xs uppercase tracking-wide text-slate-500">Cobertura operativa</p>
          <p className="mt-1 text-2xl font-semibold text-slate-900">Mexico + Espana</p>
        </div>
      </div>
    </section>
  );
}
