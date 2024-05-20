# 第一段：构建阶段
FROM node:alpine AS builder

# 设置工作目录
WORKDIR /app

# 复制 package.json 和 package-lock.json 到工作目录
COPY package*.json ./

# 安装依赖
RUN npm ci

# 复制项目代码到工作目录
COPY . .

# 构建应用
RUN npm run build

# 第二段：运行阶段
FROM nginx:alpine

# 复制 nginx 配置文件到工作目录
COPY nginx.conf /etc/nginx/nginx.conf

# 复制构建好的前端文件到 nginx 的默认目录
COPY --from=builder /app/dist /usr/share/nginx/html

# 启动 nginx
CMD ["nginx", "-g", "daemon off;"]