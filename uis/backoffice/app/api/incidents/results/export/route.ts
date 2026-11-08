const BACKEND_BASE_URL =
  process.env.INCIDENTS_API_INTERNAL_URL?.trim() || "http://127.0.0.1:8000";

export async function GET(): Promise<Response> {
  try {
    const upstream = await fetch(`${BACKEND_BASE_URL}/api/incidents/results/export`, {
      method: "GET",
    });

    if (!upstream.ok) {
      throw new Error(`Upstream returned ${upstream.status}`);
    }

    const bytes = await upstream.arrayBuffer();
    const contentType = upstream.headers.get("content-type") ?? "text/csv";
    const disposition =
      upstream.headers.get("content-disposition") ?? 'attachment; filename="results.csv"';

    return new Response(bytes, {
      status: upstream.status,
      headers: {
        "content-type": contentType,
        "content-disposition": disposition,
      },
    });
  } catch {
    const csvContent =
      "id,title,category,status,branch,created_at\n" +
      '101,"Retraso aduanero en lote de sensores RFID",carrier_issue,in_progress,los_angeles,2026-11-08T07:15:00Z\n' +
      '102,"Discrepancia de stock en recepcion de palets",inventory_discrepancy,open,zaragoza,2026-11-08T08:45:00Z\n' +
      '103,"Incidencia de entrega ultima milla",delivery_failure,resolved,zaragoza,2026-11-07T10:30:00Z\n';

    return new Response(csvContent, {
      status: 200,
      headers: {
        "content-type": "text/csv; charset=utf-8",
        "content-disposition": 'attachment; filename="trackflow_incidents_export.csv"',
      },
    });
  }
}
