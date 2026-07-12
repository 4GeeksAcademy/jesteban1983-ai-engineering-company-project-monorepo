const testimonials = [
  {
    name: "Ana Whitfield",
    role: "Operations Lead",
    quote:
      "Con una sola capa de logica para website y backoffice, redujimos reprocesos y decisiones inconsistentes.",
  },
  {
    name: "Ruben Salas",
    role: "Warehouse Supervisor",
    quote:
      "Las alertas de bajo stock nos permitieron evitar quiebres en categorias criticas durante picos de demanda.",
  },
  {
    name: "Marta Lozano",
    role: "Customer Success",
    quote:
      "La trazabilidad por estado de envio mejoro la comunicacion con clientes y la calidad del soporte.",
  },
];

export function TestimonialsSection() {
  return (
    <section id="testimonios" className="mt-14">
      <h2 className="text-2xl font-bold text-slate-900 md:text-3xl">Lo que dice el equipo</h2>
      <div className="mt-6 grid gap-4 md:grid-cols-3">
        {testimonials.map((item) => (
          <article key={item.name} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <p className="text-slate-700">&ldquo;{item.quote}&rdquo;</p>
            <p className="mt-4 font-semibold text-slate-900">{item.name}</p>
            <p className="text-sm text-slate-500">{item.role}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
