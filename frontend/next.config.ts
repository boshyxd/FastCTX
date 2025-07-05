import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  onDemandEntries: {
    maxInactiveAge: 25 * 1000,
    pagesBufferLength: 2,
  },
  devIndicators: {
    buildActivity: false,
    appIsrStatus: false,
  },
  experimental: {
    clientRouterFilter: false,
  }
};

export default nextConfig;
