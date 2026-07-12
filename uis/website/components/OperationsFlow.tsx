const steps = [
  {
    title: "1. Captura de demanda",
    detail: "El pedido entra con prioridad, destino y valor declarado.",
  },
  {
    title: "2. Validacion automatica",
    detail: "La logica valida inventario, peso, costos y restricciones de transportista.",
  },
  {
    title: "3. Seleccion optima",
    detail: "Se puntuan carriers y se elige la mejor opcion costo-servicio.",
  },
  {
    title: "4. Seguimiento continuo",
    detail: "Backoffice monitorea estado y desvios hasta la entrega final.",
  },
];

export function OperationsFlow() {
  return (
    <section id="flujo" className="mt-14">
      <h2 className="text-2xl font-bold text-slate-900 md:text-3xl">Como funciona TrackFlow</h2>
      <div className="mt-6 grid gap-4 md:grid-cols-2">
        {steps.map((step) => (
          <article key={step.title} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-slate-900">{step.title}</h3>
            <p className="mt-2 text-slate-600">{step.detail}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
