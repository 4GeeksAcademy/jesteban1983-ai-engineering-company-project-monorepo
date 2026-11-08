// lib/demo-fallback.ts — Capa de resiliencia y datos interactivos para demostración en línea (Vercel)
//
// Cuando el backoffice se despliega en Vercel sin los contenedores locales (localhost:8000 / 8003),
// esta capa proporciona estado interactivo persistido en sessionStorage para que los 8 módulos
// sean 100% navegables y funcionales durante la demostración en vivo del Capstone.

import type { Supplier } from "@/app/suppliers/types";
import type { Incident, IncidentSummary } from "@/lib/incident-actions";
import type { PipelineRun, PipelineStats, KpiRecord } from "@/lib/pipeline-actions";
import type {
  TelemetryEventRecord,
  TelemetryQueryResponse,
  TelemetrySummaryResponse,
  TelemetryReportResponse,
} from "@/lib/telemetry-api";
import type { Product, Order, InboundOrderInput, OutboundOrderInput } from "@/types/inventory";

const STORAGE_KEYS = {
  PROFILE: "tf_demo_profile",
  SUPPLIERS: "tf_demo_suppliers",
  INCIDENTS: "tf_demo_incidents",
  PRODUCTS: "tf_demo_products",
  ORDERS: "tf_demo_orders",
};

function readStorage<T>(key: string, fallback: T): T {
  if (typeof window === "undefined") return fallback;
  try {
    const raw = sessionStorage.getItem(key);
    if (!raw) {
      sessionStorage.setItem(key, JSON.stringify(fallback));
      return fallback;
    }
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}

function writeStorage<T>(key: string, data: T): void {
  if (typeof window === "undefined") return;
  try {
    sessionStorage.setItem(key, JSON.stringify(data));
  } catch {
    // ignore storage quota errors
  }
}

// ─────────────────────────────────────────────────────────────
// 1. Semillas iniciales de TrackFlow (Los Ángeles & Zaragoza)
// ─────────────────────────────────────────────────────────────

const INITIAL_SUPPLIERS: Supplier[] = [
  {
    id: 1,
    name: "Pacific West Freight LAX",
    country: "USA",
    categories: ["carrier_international", "carrier_last_mile"],
    rate_per_shipment: 145.5,
    currency: "USD",
    status: "active",
    service_zone: "Los Ángeles Port / Southern California",
    contact_email: "ops@pacificwestlax.com",
    notes: "Operador prioritario en corredor marítimo-aéreo LAX.",
    updated_at: "2026-11-08T08:30:00Z",
  },
  {
    id: 2,
    name: "Aragón Logística Plataforma PLAZA",
    country: "Spain",
    categories: ["carrier_last_mile", "reverse_logistics"],
    rate_per_shipment: 68.0,
    currency: "EUR",
    status: "active",
    service_zone: "Zaragoza PLAZA / Corredor Ebro-Madrid-Barcelona",
    contact_email: "trafico@aragonplaza.es",
    notes: "Hub central europeo en Zaragoza con distribución 24h.",
    updated_at: "2026-11-08T09:15:00Z",
  },
  {
    id: 3,
    name: "TransIberia ColdChain Packaging",
    country: "Spain",
    categories: ["packaging_materials", "warehouse_supplies"],
    rate_per_shipment: 42.75,
    currency: "EUR",
    status: "active",
    service_zone: "Península Ibérica",
    contact_email: "pedidos@transiberiacold.es",
    notes: "Suministro de embalaje isotérmico y sensores RFID.",
    updated_at: "2026-11-07T16:40:00Z",
  },
  {
    id: 4,
    name: "SoCal Fleet & WMS Systems",
    country: "USA",
    categories: ["it_and_wms_software", "fleet_maintenance"],
    rate_per_shipment: 210.0,
    currency: "USD",
    status: "active",
    service_zone: "California / Nevada",
    contact_email: "support@socalwms.io",
    notes: "Integración de telemetría IoT y mantenimiento de flota eléctrica.",
    updated_at: "2026-11-07T14:20:00Z",
  },
  {
    id: 5,
    name: "Levante Express Cargo",
    country: "Spain",
    categories: ["carrier_international"],
    rate_per_shipment: 119.0,
    currency: "EUR",
    status: "suspended",
    service_zone: "Valencia / Zaragoza",
    contact_email: "incidencias@levanteexpress.es",
    notes: "Suspendido temporalmente por auditoría de SLA trimestral.",
    updated_at: "2026-11-06T11:00:00Z",
  },
];

const INITIAL_INCIDENTS: Incident[] = [
  {
    id: 101,
    title: "Retraso aduanero en lote de sensores RFID (LAX -> ZAZ)",
    description:
      "Inspección documental adicional en terminal de carga de Los Ángeles sobre partida SKU-TF-004. Requiere validación de factura comercial por agente aduanal.",
    category: "carrier_issue",
    status: "in_progress",
    origin: "operator",
    branch: "los_angeles",
    created_at: "2026-11-08T07:15:00Z",
    updated_at: "2026-11-08T09:00:00Z",
  },
  {
    id: 102,
    title: "Discrepancia de stock en recepción de palets isotérmicos",
    description:
      "Albarán de entrada declara 200 unidades pero el conteo físico en muelle ZAZ-02 registra 188 unidades (-12 uds).",
    category: "inventory_discrepancy",
    status: "open",
    origin: "warehouse",
    branch: "zaragoza",
    created_at: "2026-11-08T08:45:00Z",
    updated_at: "2026-11-08T08:45:00Z",
  },
  {
    id: 103,
    title: "Incidencia de entrega última milla en polígono Malpica",
    description:
      "Destinatario ausente en primer intento de entrega urgente; reprogramado con ventana horaria confirmada.",
    category: "delivery_failure",
    status: "resolved",
    origin: "driver",
    branch: "zaragoza",
    created_at: "2026-11-07T10:30:00Z",
    updated_at: "2026-11-07T17:20:00Z",
  },
  {
    id: 104,
    title: "Latencia elevada en sincronización de etiquetas WMS",
    description:
      "El webhook del transportista tardó 4.2s en responder durante el pico de expedición nocturna en Los Ángeles.",
    category: "system_failure",
    status: "resolved",
    origin: "automated_alert",
    branch: "los_angeles",
    created_at: "2026-11-06T22:10:00Z",
    updated_at: "2026-11-07T01:05:00Z",
  },
  {
    id: 105,
    title: "Paquete con embalaje exterior deteriorado en tránsito",
    description:
      "Detectada deformación leve en caja master durante clasificación en hub Zaragoza; contenido verificado intacto.",
    category: "returns_issue",
    status: "open",
    origin: "client",
    branch: "zaragoza",
    created_at: "2026-11-08T10:05:00Z",
    updated_at: "2026-11-08T10:05:00Z",
  },
];

const INITIAL_PRODUCTS: Product[] = [
  {
    id: 1,
    name: "Contenedor Isotérmico SmartCool 60L",
    sku: "TF-ISO-060",
    current_stock: 142,
    category: "Cadena de Frío",
    warehouse: "Zaragoza (PLAZA)",
    price: 185.0,
    min_stock: 30,
    is_active: true,
  },
  {
    id: 2,
    name: "Tracker GPS/LTE Multi-Sensor Carga Internacional",
    sku: "TF-IOT-900",
    current_stock: 18,
    category: "Telemetría IoT",
    warehouse: "Los Ángeles (LAX-01)",
    price: 94.5,
    min_stock: 25,
    is_active: true,
  },
  {
    id: 3,
    name: "Palet Europeo Reforzado RFID (800x1200mm)",
    sku: "TF-PAL-420",
    current_stock: 310,
    category: "Almacenaje",
    warehouse: "Zaragoza (PLAZA)",
    price: 32.0,
    min_stock: 50,
    is_active: true,
  },
  {
    id: 4,
    name: "Bobina Film Estirable Industrial Bio-Tech",
    sku: "TF-PKG-110",
    current_stock: 7,
    category: "Embalaje",
    warehouse: "Zaragoza (PLAZA)",
    price: 24.9,
    min_stock: 20,
    is_active: true,
  },
  {
    id: 5,
    name: "Lector Óptico Industrial Zebra QR/RFID",
    sku: "TF-HW-550",
    current_stock: 64,
    category: "Hardware Almacén",
    warehouse: "Los Ángeles (LAX-01)",
    price: 340.0,
    min_stock: 15,
    is_active: true,
  },
  {
    id: 6,
    name: "Precinto de Seguridad de Alta Resistencia ISO-17712",
    sku: "TF-SEC-800",
    current_stock: 0,
    category: "Seguridad Aduanera",
    warehouse: "Los Ángeles (LAX-01)",
    price: 3.5,
    min_stock: 100,
    is_active: true,
  },
];

const INITIAL_ORDERS: Order[] = [
  {
    id: 501,
    product_id: 1,
    product_name: "Contenedor Isotérmico SmartCool 60L",
    quantity: 50,
    order_type: "inbound",
    created_at: "2026-11-08T08:15:00Z",
    user_uuid: "op-zaragoza-01",
  },
  {
    id: 502,
    product_id: 2,
    product_name: "Tracker GPS/LTE Multi-Sensor Carga Internacional",
    quantity: 12,
    order_type: "outbound",
    created_at: "2026-11-08T09:40:00Z",
    user_uuid: "op-lax-04",
  },
  {
    id: 503,
    product_id: 3,
    product_name: "Palet Europeo Reforzado RFID (800x1200mm)",
    quantity: 80,
    order_type: "inbound",
    created_at: "2026-11-07T16:20:00Z",
    user_uuid: "op-zaragoza-01",
  },
  {
    id: 504,
    product_id: 5,
    product_name: "Lector Óptico Industrial Zebra QR/RFID",
    quantity: 6,
    order_type: "outbound",
    created_at: "2026-11-07T11:10:00Z",
    user_uuid: "op-lax-02",
  },
];

const DEMO_PIPELINE_RUNS: PipelineRun[] = [
  {
    run_id: "run_20261108_0600_zaz",
    pipeline_name: "telemetry_to_warehouse_kpis",
    status: "completed",
    started_at: "2026-11-08T06:00:00Z",
    finished_at: "2026-11-08T06:01:42Z",
    rows_read: 14820,
    rows_upserted: 14820,
    error_message: null,
    triggered_by: "celery_beat_nightly",
    week_start: "2026-11-02",
  },
  {
    run_id: "run_20261107_1800_lax",
    pipeline_name: "telemetry_to_warehouse_kpis",
    status: "completed",
    started_at: "2026-11-07T18:00:00Z",
    finished_at: "2026-11-07T18:01:19Z",
    rows_read: 12350,
    rows_upserted: 12350,
    error_message: null,
    triggered_by: "manual_backoffice",
    week_start: "2026-11-02",
  },
  {
    run_id: "run_20261107_0600_zaz",
    pipeline_name: "supplier_sla_reconciliation",
    status: "completed",
    started_at: "2026-11-07T06:00:00Z",
    finished_at: "2026-11-07T06:00:54Z",
    rows_read: 9410,
    rows_upserted: 9402,
    error_message: null,
    triggered_by: "celery_beat_nightly",
    week_start: "2026-10-26",
  },
  {
    run_id: "run_20261106_0600_lax",
    pipeline_name: "telemetry_to_warehouse_kpis",
    status: "failed",
    started_at: "2026-11-06T06:00:00Z",
    finished_at: "2026-11-06T06:00:18Z",
    rows_read: 3100,
    rows_upserted: 0,
    error_message: "Timeout transitorio en nodo réplica PostgreSQL; reintentado con éxito en siguiente ventana.",
    triggered_by: "celery_beat_nightly",
    week_start: "2026-10-26",
  },
];

const DEMO_KPIS: KpiRecord[] = [
  {
    id: "kpi-zaz-2026w45",
    warehouse: "zaragoza",
    client_id: "TF-EU-GLOBAL",
    week_start: "2026-11-02",
    inbound_units_count: 8420,
    outbound_orders_count: 1295,
    stockout_events_count: 1,
    discrepancy_events_count: 6,
    discrepancy_rate: 0.0046,
    computed_at: "2026-11-08T06:01:42Z",
  },
  {
    id: "kpi-lax-2026w45",
    warehouse: "los_angeles",
    client_id: "TF-US-WEST",
    week_start: "2026-11-02",
    inbound_units_count: 11250,
    outbound_orders_count: 1840,
    stockout_events_count: 2,
    discrepancy_events_count: 9,
    discrepancy_rate: 0.0049,
    computed_at: "2026-11-08T06:01:42Z",
  },
  {
    id: "kpi-zaz-2026w44",
    warehouse: "zaragoza",
    client_id: "TF-EU-GLOBAL",
    week_start: "2026-10-26",
    inbound_units_count: 7890,
    outbound_orders_count: 1180,
    stockout_events_count: 0,
    discrepancy_events_count: 3,
    discrepancy_rate: 0.0025,
    computed_at: "2026-11-01T06:01:10Z",
  },
];

// ─────────────────────────────────────────────────────────────
// 2. Manejador de rutas para lib/api.ts (Auth, Incidentes, Pipeline, Suppliers)
// ─────────────────────────────────────────────────────────────

export function handleDemoApiRequest<T>(
  method: "GET" | "POST" | "PUT" | "PATCH",
  path: string,
  body?: Record<string, unknown>
): T {
  const cleanPath = path.split("?")[0];
  const queryString = path.includes("?") ? path.split("?")[1] : "";
  const params = new URLSearchParams(queryString);

  // --- AUTH & PROFILE ---
  if (cleanPath === "/auth/login" && method === "POST") {
    const email = String(body?.email || "admin@trackflow.com");
    const profile = readStorage(STORAGE_KEYS.PROFILE, {
      email,
      role: "admin",
      is_active: true,
      profile: {
        name: "Jonathan Esteban (TrackFlow Admin)",
        phone: "+34 976 001 122",
        address: "Plataforma Logística PLAZA, Zaragoza / LAX Hub",
      },
    });
    profile.email = email;
    writeStorage(STORAGE_KEYS.PROFILE, profile);
    return {
      access_token: "demo-jwt-trackflow-capstone",
      token_type: "bearer",
    } as unknown as T;
  }

  if ((cleanPath === "/users/" || cleanPath === "/users") && method === "POST") {
    const email = String(body?.email || "admin@trackflow.com");
    const name = String(body?.name || "Jonathan Esteban");
    const profile = {
      email,
      role: "admin",
      is_active: true,
      profile: {
        name,
        phone: String(body?.phone || "+34 976 001 122"),
        address: String(body?.address || "Zaragoza PLAZA / Los Ángeles"),
      },
    };
    writeStorage(STORAGE_KEYS.PROFILE, profile);
    return { id: 1, ...profile } as unknown as T;
  }

  if (cleanPath === "/auth/me" && method === "GET") {
    return readStorage(STORAGE_KEYS.PROFILE, {
      email: "admin@trackflow.com",
      role: "admin",
      is_active: true,
      profile: {
        name: "Jonathan Esteban (TrackFlow Admin)",
        phone: "+34 976 001 122",
        address: "Plataforma Logística PLAZA, Zaragoza / LAX Hub",
      },
    }) as unknown as T;
  }

  if (cleanPath === "/profiles/me" && method === "PUT") {
    const current = readStorage(STORAGE_KEYS.PROFILE, {
      email: "admin@trackflow.com",
      role: "admin",
      is_active: true,
      profile: {
        name: "Jonathan Esteban (TrackFlow Admin)",
        phone: "+34 976 001 122",
        address: "Plataforma Logística PLAZA, Zaragoza / LAX Hub",
      },
    });
    const updated = {
      ...current,
      profile: {
        name: body?.name !== undefined ? String(body.name) : current.profile.name,
        phone: body?.phone !== undefined ? String(body.phone) : current.profile.phone,
        address: body?.address !== undefined ? String(body.address) : current.profile.address,
      },
    };
    writeStorage(STORAGE_KEYS.PROFILE, updated);
    return {
      id: 1,
      user_id: 1,
      ...updated.profile,
    } as unknown as T;
  }

  if (cleanPath.startsWith("/auth/")) {
    return { message: "Operación procesada correctamente." } as unknown as T;
  }

  // --- INCIDENTS ---
  if (cleanPath === "/api/incidents/summary" && method === "GET") {
    const incidents = readStorage<Incident[]>(STORAGE_KEYS.INCIDENTS, INITIAL_INCIDENTS);
    const summary: IncidentSummary = {
      by_status: {},
      by_category: {},
      by_origin: {},
      by_branch: {},
    };
    for (const inc of incidents) {
      summary.by_status[inc.status] = (summary.by_status[inc.status] || 0) + 1;
      summary.by_category[inc.category] = (summary.by_category[inc.category] || 0) + 1;
      summary.by_origin[inc.origin] = (summary.by_origin[inc.origin] || 0) + 1;
      summary.by_branch[inc.branch] = (summary.by_branch[inc.branch] || 0) + 1;
    }
    return summary as unknown as T;
  }

  if ((cleanPath === "/api/incidents/" || cleanPath === "/api/incidents") && method === "GET") {
    let incidents = [...readStorage<Incident[]>(STORAGE_KEYS.INCIDENTS, INITIAL_INCIDENTS)];
    const status = params.get("status");
    const category = params.get("category");
    const origin = params.get("origin");
    const branch = params.get("branch");
    if (status) incidents = incidents.filter((i) => i.status === status);
    if (category) incidents = incidents.filter((i) => i.category === category);
    if (origin) incidents = incidents.filter((i) => i.origin === origin);
    if (branch) incidents = incidents.filter((i) => i.branch === branch);
    return incidents as unknown as T;
  }

  if ((cleanPath === "/api/incidents/" || cleanPath === "/api/incidents") && method === "POST") {
    const incidents = readStorage<Incident[]>(STORAGE_KEYS.INCIDENTS, INITIAL_INCIDENTS);
    const now = new Date().toISOString();
    const newInc: Incident = {
      id: Date.now(),
      title: String(body?.title || "Nueva incidencia operativa"),
      description: String(body?.description || ""),
      category: String(body?.category || "other"),
      status: "open",
      origin: String(body?.origin || "operator"),
      branch: String(body?.branch || "zaragoza"),
      created_at: now,
      updated_at: now,
    };
    const next = [newInc, ...incidents];
    writeStorage(STORAGE_KEYS.INCIDENTS, next);
    return newInc as unknown as T;
  }

  const incidentStatusMatch = cleanPath.match(/^\/api\/incidents\/(\d+)\/status$/);
  if (incidentStatusMatch && method === "PATCH") {
    const id = Number(incidentStatusMatch[1]);
    const incidents = readStorage<Incident[]>(STORAGE_KEYS.INCIDENTS, INITIAL_INCIDENTS);
    const updated = incidents.map((inc) =>
      inc.id === id
        ? { ...inc, status: String(body?.status || inc.status), updated_at: new Date().toISOString() }
        : inc
    );
    writeStorage(STORAGE_KEYS.INCIDENTS, updated);
    const found = updated.find((i) => i.id === id) || updated[0];
    return found as unknown as T;
  }

  // --- PIPELINE ETL ---
  if (cleanPath === "/pipeline/stats") {
    const stats: PipelineStats = {
      total_runs: 42,
      completed_runs: 40,
      failed_runs: 2,
      success_rate: 95.2,
      last_run: DEMO_PIPELINE_RUNS[0],
      rows_read_total: 486290,
      rows_upserted_total: 485110,
      weeks_with_kpis: 12,
    };
    return stats as unknown as T;
  }

  if (cleanPath === "/pipeline/latest-runs" || cleanPath === "/pipeline/runs") {
    return DEMO_PIPELINE_RUNS as unknown as T;
  }

  if (cleanPath === "/pipeline/kpis") {
    const weekStart = params.get("week_start");
    const list = weekStart ? DEMO_KPIS.filter((k) => k.week_start === weekStart) : DEMO_KPIS;
    return list as unknown as T;
  }

  return {} as T;
}

// ─────────────────────────────────────────────────────────────
// 3. Manejador de Proveedores (SuppliersClient)
// ─────────────────────────────────────────────────────────────

export function getDemoSuppliers(country?: string, category?: string): Supplier[] {
  let list = [...readStorage<Supplier[]>(STORAGE_KEYS.SUPPLIERS, INITIAL_SUPPLIERS)];
  if (country) list = list.filter((s) => s.country === country);
  if (category) list = list.filter((s) => s.categories.includes(category));
  return list;
}

export function toggleDemoSupplierStatus(id: number, newStatus: "active" | "suspended"): Supplier[] {
  const list = readStorage<Supplier[]>(STORAGE_KEYS.SUPPLIERS, INITIAL_SUPPLIERS);
  const updated = list.map((s) =>
    s.id === id ? { ...s, status: newStatus, updated_at: new Date().toISOString() } : s
  );
  writeStorage(STORAGE_KEYS.SUPPLIERS, updated);
  return updated;
}

export function updateDemoSupplierRate(id: number, newRate: number): Supplier {
  const list = readStorage<Supplier[]>(STORAGE_KEYS.SUPPLIERS, INITIAL_SUPPLIERS);
  const updated = list.map((s) =>
    s.id === id ? { ...s, rate_per_shipment: newRate, updated_at: new Date().toISOString() } : s
  );
  writeStorage(STORAGE_KEYS.SUPPLIERS, updated);
  return updated.find((s) => s.id === id) || updated[0];
}

export function createDemoSupplier(payload: Partial<Supplier>): Supplier {
  const list = readStorage<Supplier[]>(STORAGE_KEYS.SUPPLIERS, INITIAL_SUPPLIERS);
  const created: Supplier = {
    id: Date.now(),
    name: String(payload.name || "Nuevo Proveedor Logístico"),
    country: (payload.country as "USA" | "Spain") || "Spain",
    categories: Array.isArray(payload.categories) ? payload.categories : ["carrier_last_mile"],
    rate_per_shipment: Number(payload.rate_per_shipment || 75),
    currency: payload.country === "USA" ? "USD" : "EUR",
    status: "active",
    service_zone: payload.service_zone || "Nacional",
    contact_email: payload.contact_email || "contacto@proveedor.com",
    updated_at: new Date().toISOString(),
  };
  writeStorage(STORAGE_KEYS.SUPPLIERS, [...list, created]);
  return created;
}

// ─────────────────────────────────────────────────────────────
// 4. Manejador de Inventario (Productos y Órdenes)
// ─────────────────────────────────────────────────────────────

export function getDemoProducts(): Product[] {
  return readStorage<Product[]>(STORAGE_KEYS.PRODUCTS, INITIAL_PRODUCTS);
}

export function getDemoProduct(id: number): Product {
  const products = getDemoProducts();
  return products.find((p) => p.id === id) || products[0];
}

export function getDemoOrders(): Order[] {
  return readStorage<Order[]>(STORAGE_KEYS.ORDERS, INITIAL_ORDERS);
}

export function createDemoOrder(
  orderType: "inbound" | "outbound",
  input: InboundOrderInput | OutboundOrderInput
): Order {
  const products = getDemoProducts();
  const orders = getDemoOrders();
  const product = products.find((p) => p.id === Number(input.product_id)) || products[0];

  if (orderType === "outbound" && product.current_stock < input.quantity) {
    throw new Error(
      `Stock insuficiente para ${product.name} (disponible: ${product.current_stock}, solicitado: ${input.quantity})`
    );
  }

  const updatedProducts = products.map((p) =>
    p.id === product.id
      ? {
          ...p,
          current_stock:
            orderType === "inbound"
              ? p.current_stock + Number(input.quantity)
              : Math.max(0, p.current_stock - Number(input.quantity)),
        }
      : p
  );
  writeStorage(STORAGE_KEYS.PRODUCTS, updatedProducts);

  const newOrder: Order = {
    id: Date.now(),
    product_id: product.id,
    product_name: product.name,
    quantity: Number(input.quantity),
    order_type: orderType,
    created_at: new Date().toISOString(),
    user_uuid: "admin-capstone",
  };
  writeStorage(STORAGE_KEYS.ORDERS, [newOrder, ...orders]);
  return newOrder;
}

// ─────────────────────────────────────────────────────────────
// 5. Manejador de Telemetría (Summary, Events, Pandas Report)
// ─────────────────────────────────────────────────────────────

const DEMO_TELEMETRY_EVENTS: TelemetryEventRecord[] = [
  {
    id: "evt-901",
    timestamp: "2026-11-08T11:45:12Z",
    service: "api",
    event_type: "http_request",
    level: "info",
    value: 18.4,
    message: "GET /api/incidents/ completado en 18.4ms",
    tags: { status_code: 200, endpoint: "/api/incidents", region: "zaragoza" },
  },
  {
    id: "evt-902",
    timestamp: "2026-11-08T11:42:05Z",
    service: "backoffice",
    event_type: "page_view",
    level: "info",
    value: 1,
    message: "Navegación a /backoffice/inventory/products",
    tags: { page: "/backoffice/inventory/products", user_role: "admin" },
  },
  {
    id: "evt-903",
    timestamp: "2026-11-08T11:38:50Z",
    service: "api",
    event_type: "ai_guardrail_check",
    level: "warn",
    value: 4.2,
    message: "Redacción automática de PII (email) aplicada antes de inferencia LLM",
    tags: { framework: "NIST-CSF-2.0", rule: "PII_EMAIL_REDACTED" },
  },
  {
    id: "evt-904",
    timestamp: "2026-11-08T11:30:19Z",
    service: "api",
    event_type: "agent_execution",
    level: "info",
    value: 340.5,
    message: "Ejecución grafo LangGraph (router -> retriever -> synthesizer)",
    tags: { nodes: 3, warehouse: "los_angeles" },
  },
  {
    id: "evt-905",
    timestamp: "2026-11-08T11:15:00Z",
    service: "api",
    event_type: "prompt_injection_blocked",
    level: "error",
    value: 1,
    message: "Intento de Prompt Injection bloqueado por PromptInjectionGuard",
    tags: { threat_level: "HIGH", ip: "192.0.2.44" },
  },
];

export function getDemoTelemetrySummary(): TelemetrySummaryResponse {
  return {
    total_events: 1842,
    by_event_type: [
      { label: "http_request", count: 890 },
      { label: "page_view", count: 520 },
      { label: "agent_execution", count: 215 },
      { label: "ai_guardrail_check", count: 185 },
      { label: "prompt_injection_blocked", count: 32 },
    ],
    by_service: [
      { label: "api", count: 1180 },
      { label: "backoffice", count: 662 },
    ],
    by_level: [
      { label: "info", count: 1625 },
      { label: "warn", count: 185 },
      { label: "error", count: 32 },
    ],
    by_day: [
      { label: "2026-11-04", count: 310 },
      { label: "2026-11-05", count: 345 },
      { label: "2026-11-06", count: 390 },
      { label: "2026-11-07", count: 412 },
      { label: "2026-11-08", count: 385 },
    ],
    recent_events: DEMO_TELEMETRY_EVENTS,
  };
}

export function getDemoTelemetryEvents(params?: {
  event_type?: string;
  service?: string;
  level?: string;
}): TelemetryQueryResponse {
  let list = [...DEMO_TELEMETRY_EVENTS];
  if (params?.event_type) list = list.filter((e) => e.event_type === params.event_type);
  if (params?.service) list = list.filter((e) => e.service === params.service);
  if (params?.level) list = list.filter((e) => e.level === params.level);
  return {
    events: list,
    total: list.length,
    limit: 50,
    offset: 0,
  };
}

export function getDemoTelemetryReport(): TelemetryReportResponse {
  return {
    period: {
      from: "2026-11-02T00:00:00Z",
      to: "2026-11-08T23:59:59Z",
    },
    metrics: {
      events_per_day: [
        { date: "2026-11-04", count: 310 },
        { date: "2026-11-05", count: 345 },
        { date: "2026-11-06", count: 390 },
        { date: "2026-11-07", count: 412 },
        { date: "2026-11-08", count: 385 },
      ],
      error_rate_by_type: [
        { event_type: "prompt_injection_blocked", count: 32, percentage: 1.74 },
        { event_type: "http_request", count: 14, percentage: 0.76 },
      ],
      events_by_service: [
        { service: "api", count: 1180, avg_value: 24.6 },
        { service: "backoffice", count: 662, avg_value: 1.2 },
      ],
      level_distribution: [
        { level: "info", count: 1625 },
        { level: "warn", count: 185 },
        { level: "error", count: 32 },
      ],
      daily_error_trend: [
        { date: "2026-11-04", error_count: 5 },
        { date: "2026-11-05", error_count: 8 },
        { date: "2026-11-06", error_count: 7 },
        { date: "2026-11-07", error_count: 6 },
        { date: "2026-11-08", error_count: 6 },
      ],
    },
  };
}

// ─────────────────────────────────────────────────────────────
// 6. Respuestas RAG y Agente LangGraph para Demo en Línea
// ─────────────────────────────────────────────────────────────

export function getDemoKnowledgeAnswer(question: string): string {
  const q = question.toLowerCase();
  if (q.includes("plazo") || q.includes("entrega") || q.includes("sla")) {
    return (
      "Según el Manual Operativo de TrackFlow (Sección 4.2 — SLAs de Transporte):\n" +
      "• Corredor Ibérico (Zaragoza PLAZA → Península): 24 horas para envíos estándar y 12 horas para carga crítica isotérmica.\n" +
      "• Corredor Transatlántico (Los Ángeles LAX → Zaragoza ZAZ): 48-72 horas vía carga aérea consolidada y 14 días en contenedor marítimo.\n" +
      "• Margen de discrepancia máximo permitido por proveedor: 0.5% por lote."
    );
  }
  if (q.includes("incidencia") || q.includes("aduana") || q.includes("stock")) {
    return (
      "Protocolo de Gestión de Incidencias y Stock (Normativa TF-OPS-2026):\n" +
      "1. Toda discrepancia de inventario > 2% en recepción genera alerta automática en el módulo de Incidencias.\n" +
      "2. Los artículos con stock por debajo de `min_stock` activan orden de reaprovisionamiento sugerida.\n" +
      "3. Acciones destructivas o purgas de inventario requieren aprobación explícita mediante Human-in-the-Loop (HITL) bajo el marco NIST CSF 2.0."
    );
  }
  return (
    `Base de Conocimiento Vectorial (Qdrant) — Resultado para "${question}":\n` +
    "TrackFlow opera dos hubs logísticos principales: Los Ángeles (LAX-01) y Zaragoza (PLAZA). " +
    "Todas las operaciones de entrada (inbound) y salida (outbound) quedan auditadas en tiempo real, " +
    "con validación de esquemas Pydantic V2, pipeline nocturno Celery/Redis hacia reporting.db y guardrails deterministas de seguridad IA."
  );
}

export function getDemoAgentResponse(question: string): {
  answer: string;
  run_id: string;
  trace: Record<string, unknown>;
} {
  const q = question.toLowerCase();
  const runId = "lg_run_" + Math.random().toString(36).substring(2, 9);
  const now = new Date().toISOString();

  let answer =
    "He consultado las herramientas operativas de TrackFlow:\n" +
    "• Almacén Zaragoza (PLAZA): 459 unidades activas en 3 líneas de SKU (1 alerta de stock bajo en Bobina Film Bio-Tech con 7 uds).\n" +
    "• Almacén Los Ángeles (LAX-01): 82 unidades activas (alerta crítica: Precinto ISO-17712 agotado y Tracker GPS bajo mínimo con 18 uds).\n" +
    "• Incidencias abiertas: 2 pendientes de resolución y 1 en progreso en aduana LAX.";

  if (q.includes("incidencia")) {
    answer =
      "Resumen de Incidencias Activas en TrackFlow:\n" +
      "1. [ID #101 - En Progreso] Retraso aduanero en lote de sensores RFID (Sucursal: Los Ángeles).\n" +
      "2. [ID #102 - Abierta] Discrepancia de stock en recepción de palets isotérmicos (-12 uds en muelle ZAZ-02).\n" +
      "3. [ID #105 - Abierta] Paquete con embalaje exterior deteriorado en tránsito (Zaragoza).\n" +
      "Recomendación del agente: Priorizar validación documental de la incidencia #101 con Pacific West Freight LAX.";
  } else if (q.includes("proveedor") || q.includes("rfp") || q.includes("tarifa")) {
    answer =
      "Evaluación Multi-Agente de Proveedores (Routing -> Evaluator-Optimizer):\n" +
      "• USA (LAX): Pacific West Freight ($145.50/envío, SLA 99.1%, Activo) y SoCal Fleet & WMS ($210.00/envío, Activo).\n" +
      "• España (Zaragoza): Aragón Logística PLAZA (€68.00/envío, SLA 99.4%, Activo) y TransIberia ColdChain (€42.75/envío, Activo).\n" +
      "• Nota de cumplimiento: Levante Express Cargo se encuentra suspendido hasta superar auditoría trimestral.";
  }

  return {
    answer,
    run_id: runId,
    trace: {
      run_id: runId,
      question,
      timestamp: now,
      framework: "LangGraph + TrackFlow MCP Tools + NIST Guardrails",
      nodes: [
        {
          node: "input_guardrail_nist",
          status: "passed",
          latency_ms: 3.1,
          output: { injection_detected: false, pii_redacted: false },
        },
        {
          node: "intent_router",
          status: "completed",
          latency_ms: 14.8,
          output: { route: "warehouse_operations_and_rag" },
        },
        {
          node: "mcp_tool_executor",
          status: "completed",
          latency_ms: 42.3,
          tools_called: ["get_warehouse_stock", "list_active_incidents", "query_qdrant_rag"],
        },
        {
          node: "evaluator_optimizer_synthesizer",
          status: "completed",
          latency_ms: 89.4,
          quality_score: 0.98,
        },
      ],
    },
  };
}

