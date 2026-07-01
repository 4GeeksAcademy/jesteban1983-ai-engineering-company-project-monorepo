import { Product } from "@trackflow/logic/src/trackflow/contracts";

interface ProductCatalogProps {
  products: Product[];
  title: string;
}

export function ProductCatalog({ products, title }: ProductCatalogProps) {
  if (products.length === 0) return <p>No hay productos disponibles.</p>;

  return (
    <section className="my-8">
      <h2 className="text-2xl font-bold mb-4">{title}</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {products.map((product) => (
          <div key={product.id} className="p-4 border rounded shadow-sm">
            <h3 className="font-semibold">{product.name}</h3>
            <p className="text-sm text-gray-600">Stock: {product.stockQuantity}</p>
            <span className="text-xs bg-gray-200 px-2 py-1 rounded">{product.category}</span>
          </div>
        ))}
      </div>
    </section>
  );
}