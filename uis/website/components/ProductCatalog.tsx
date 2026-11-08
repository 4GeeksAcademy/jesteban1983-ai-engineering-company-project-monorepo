import { Product } from "@trackflow/logic";

interface ProductCatalogProps {
  products: Product[];
  title: string;
}

export function ProductCatalog({ products, title }: ProductCatalogProps) {
  if (products.length === 0) {
    return (
      <section className="mt-14 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-2xl font-bold text-slate-900">{title}</h2>
        <p className="mt-3 text-slate-600">No hay productos con alertas activas.</p>
      </section>
    );
  }

  return (
    <section className="mt-14">
      <h2 className="text-2xl font-bold text-slate-900 md:text-3xl">{title}</h2>
      <p className="mt-2 text-slate-600">
        Productos que requieren accion inmediata para evitar ruptura de disponibilidad.
      </p>
      <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-3">
        {products.map((product) => (
          <article key={product.id} className="rounded-2xl border border-amber-200 bg-amber-50 p-5 shadow-sm">
            <h3 className="text-lg font-semibold text-slate-900">{product.name}</h3>
            <p className="mt-1 text-sm text-slate-700">SKU: {product.sku}</p>
            <p className="mt-2 text-sm text-slate-700">
              Stock actual: <span className="font-semibold">{product.stockQuantity}</span>
            </p>
            <p className="text-sm text-slate-700">Umbral minimo: {product.minStockThreshold}</p>
            <span className="mt-3 inline-block rounded-full bg-white px-3 py-1 text-xs font-medium text-slate-700">
              {product.category}
            </span>
          </article>
        ))}
      </div>
    </section>
  );
}