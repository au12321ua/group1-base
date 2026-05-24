import { defineConfig, type Plugin } from "vite";
import vue from "@vitejs/plugin-vue";
import { resolve } from "path";
import { randomUUID } from "node:crypto";

/** 开发网关插件 —— 为 Info Service 注入身份 Header */
function devGatewayPlugin(): Plugin {
  return {
    name: "dev-gateway",
    configureServer(server) {
      server.middlewares.use(async (req, res, next) => {
        // 仅拦截 Info Service 请求
        if (!req.url?.startsWith("/api/")) {
          return next();
        }

        const authHeader = req.headers["authorization"];
        if (!authHeader?.startsWith("Bearer ")) {
          return next(); // 无 Token，交由 Info Service 自行处理
        }

        const token = authHeader.slice(7);

        try {
          const verifyUrl = "http://localhost:8001/api/v1/internal/verify";
          const response = await fetch(verifyUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ token }),
          });

          if (!response.ok) {
            res.statusCode = 401;
            res.setHeader("Content-Type", "application/json");
            res.end(JSON.stringify({ code: 1001, message: "Token 验证失败" }));
            return;
          }

          const result = await response.json();
          const identity = result.data;

          // 注入身份 Header（Info Service 信任这些 Header）
          req.headers["x-user-id"] = identity.user_id;
          req.headers["x-user-role"] = identity.role;
          req.headers["x-user-permissions"] = (identity.permissions ?? []).join(",");

          // 生成链路追踪 ID
          req.headers["x-request-id"] = randomUUID();
        } catch {
          res.statusCode = 502;
          res.setHeader("Content-Type", "application/json");
          res.end(JSON.stringify({ code: 5020, message: "Auth Service 不可达" }));
          return;
        }

        next();
      });
    },
  };
}

export default defineConfig({
  plugins: [devGatewayPlugin(), vue()],
  resolve: {
    alias: {
      "@": resolve(__dirname, "src"),
    },
  },
  server: {
    port: 5173,
    proxy: {
      "/auth": {
        target: "http://localhost:8001",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/auth/, "/api/v1/auth"),
      },
      "/api": {
        target: "http://localhost:8002",
        changeOrigin: true,
      },
    },
  },
});
