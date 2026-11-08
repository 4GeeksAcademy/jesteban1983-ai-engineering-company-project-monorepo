interface KpiBandProps {
  avgDistance: number;
  topCarrierName: string;
  topCarrierUsage: number;
}

export function KpiBand({ avgDistance, topCarrierName, topCarrierUsage }: KpiBandProps) {
  return (
    <section className="mt-14 rounded-3xl border border-slate-200 bg-slate-900 px-6 py-8 text-white md:px-10">
      <h2 className="text-2xl font-bold md:text-3xl">Indicadores operativos</h2>
      <div className="mt-6 grid gap-4 md:grid-cols-3">
        <div className="rounded-2xl border border-white/20 bg-white/5 p-4">
          <p className="text-xs uppercase tracking-wider text-slate-300">Distancia promedio</p>
          <p className="mt-1 text-2xl font-semibold">{avgDistance} km</p>
        </div>
        <div className="rounded-2xl border border-white/20 bg-white/5 p-4">
          <p className="text-xs uppercase tracking-wider text-slate-300">Transportista top</p>
          <p className="mt-1 text-2xl font-semibold">{topCarrierName}</p>
        </div>
        <div className="rounded-2xl border border-white/20 bg-white/5 p-4">
          <p className="text-xs uppercase tracking-wider text-slate-300">Uso mensual</p>
          <p className="mt-1 text-2xl font-semibold">{topCarrierUsage} envios</p>
        </div>
      </div>
    </section>
  );
}
