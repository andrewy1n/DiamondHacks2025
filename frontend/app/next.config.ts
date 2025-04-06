import type { NextConfig } from "next";
const { withAuth } = require('@auth0/nextjs-auth0');

const nextConfig: NextConfig = {
  /* config options here */
};

export default nextConfig;

module.exports = {
  allowedDevOrigins: ['local-origin.dev', '*.local-origin.dev'],
}