# Stage 1: Build the Angular application
FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Copy built Angular app to Nginx serve directory
COPY --from=build /app/dist/recrulink-frontend/browser /usr/share/nginx/html

# Custom Nginx configuration for Angular routing + API proxy
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]