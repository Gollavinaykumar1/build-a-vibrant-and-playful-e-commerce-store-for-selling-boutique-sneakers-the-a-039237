import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  base: "/build-a-vibrant-and-playful-e-commerce-store-for-selling-boutique-sneakers-the-a-039237/",
  build: { outDir: "dist", assetsDir: "assets" },
  server: { port: 3000 },
});
