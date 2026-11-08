import type { NextConfig } from "next";

const API_URL = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const INVENTORY_API_URL = process.env.NEXT_PUBLIC_INVENTORY_API_URL || "http://localhost:8003";

const nextConfig: NextConfig = {
  transpilePackages: ["@trackflow/logic"],
  async rewrites() {
    return [
      {
        source: "/suppliers/:path*",
        destination: `${API_URL}/suppliers/:path*`,
      },
      {
        source: "/auth/:path*",
        destination: `${API_URL}/auth/:path*`,
      },
      {
        source: "/users/:path*",
        destination: `${API_URL}/users/:path*`,
      },
      {
        source: "/profiles/:path*",
        destination: `${API_URL}/profiles/:path*`,
      },
      {
        source: "/api/incidents/:path*",
        destination: `${API_URL}/api/incidents/:path*`,
      },
      {
        source: "/telemetry/:path*",
        destination: `${API_URL}/telemetry/:path*`,
      },
      {
        source: "/pipeline/:path*",
        destination: `${API_URL}/pipeline/:path*`,
      },
      {
        source: "/knowledge/:path*",
        destination: `${API_URL}/knowledge/:path*`,
      },
      {
        source: "/agent/:path*",
        destination: `${API_URL}/agent/:path*`,
      },
      {
        source: "/api/notifications/:path*",
        destination: `${API_URL}/api/notifications/:path*`,
      },
      {
        source: "/api/chat/:path*",
        destination: `${API_URL}/api/chat/:path*`,
      },
      {
        source: "/api/ai-security/:path*",
        destination: `${API_URL}/api/ai-security/:path*`,
      },
      {
        source: "/api/v1/:path*",
        destination: `${INVENTORY_API_URL}/api/v1/:path*`,
      },
    ];
  },
};

export default nextConfig;
