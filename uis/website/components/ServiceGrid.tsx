const services = [
  {
    title: "Control de inventario",
    description:
      "Monitoreo de stock por SKU, categoria y almacen para anticipar quiebres y priorizar reposicion.",
  },
  {
    title: "Optimizacion de envios",
    description:
      "Seleccion de transportista por score operativo y costo para cada despacho de ultima milla.",
  },
  {
    title: "Visibilidad en tiempo real",
    description:
      "Estado de pedidos y alertas de riesgo para equipos de operaciones y atencion al cliente.",
  },
  {
    title: "Analitica operativa",
    description:
      "KPIs de distancia promedio, confiabilidad y distribucion de estados para mejora continua.",
  },
];

export function ServiceGrid() {
  return (
    <section id="servicios" className="mt-14">
      <h2 className="text-2xl font-bold text-slate-900 md:text-3xl">Servicios principales</h2>
      <p className="mt-2 max-w-2xl text-slate-600">
        La plataforma combina automatizacion, reglas de negocio y trazabilidad para operaciones logisticas.
      </p>
      <div className="mt-6 grid gap-4 md:grid-cols-2">
        {services.map((service) => (
          <article key={service.title} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-slate-900">{service.title}</h3>
            <p className="mt-2 text-slate-600">{service.description}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
