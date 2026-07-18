export function CtaSection() {
  return (
    <section id="contacto" className="mt-14 rounded-3xl border border-emerald-200 bg-emerald-50 px-6 py-10 md:px-10">
      <h2 className="text-2xl font-bold text-emerald-900 md:text-3xl">Solicita una demo operativa</h2>
      <p className="mt-3 max-w-2xl text-emerald-900/80">
        Te mostramos como integrar tus reglas logisticas en una sola capa de negocio para website,
        backoffice y futuras APIs en servicios.
      </p>
      <div className="mt-6 flex flex-wrap gap-3">
        <a
          href="mailto:ops@trackflow.example"
          className="rounded-xl bg-emerald-700 px-5 py-3 font-semibold text-white transition hover:bg-emerald-800"
        >
          Contactar equipo de operaciones
        </a>
        <a
          href="#servicios"
          className="rounded-xl border border-emerald-700 px-5 py-3 font-semibold text-emerald-700 transition hover:bg-emerald-100"
        >
          Ver servicios
        </a>
      </div>
    </section>
  );
}
