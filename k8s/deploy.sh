#!/bin/bash
set -e

REGISTRY="ghcr.io/rsuguiura-crwv"
TAG="${1:-latest}"

echo "=== Building images (tag: $TAG) ==="

# Build backend
echo "Building backend..."
docker build -t "$REGISTRY/hooli-heard-backend:$TAG" ./backend

# Build frontend (production nginx)
echo "Building frontend..."
docker build -t "$REGISTRY/hooli-heard-frontend:$TAG" ./frontend

# Build seed image (from repo root)
echo "Building seed..."
docker build -t "$REGISTRY/hooli-heard-seed:$TAG" -f Dockerfile.seed .

echo ""
echo "=== Pushing images ==="
docker push "$REGISTRY/hooli-heard-backend:$TAG"
docker push "$REGISTRY/hooli-heard-frontend:$TAG"
docker push "$REGISTRY/hooli-heard-seed:$TAG"

echo ""
echo "=== Deploying to CKS ==="
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/postgres.yaml

echo "Waiting for Postgres to be ready..."
kubectl -n hooli-heard wait --for=condition=ready pod -l app=postgres --timeout=120s

kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml

echo "Waiting for backend to be ready..."
kubectl -n hooli-heard wait --for=condition=available deployment/backend --timeout=120s

echo ""
echo "=== Seeding database ==="
# Delete old seed job if it exists
kubectl -n hooli-heard delete job seed-db --ignore-not-found
kubectl apply -f k8s/seed-job.yaml

echo "Waiting for seed to complete..."
kubectl -n hooli-heard wait --for=condition=complete job/seed-db --timeout=120s

echo ""
echo "=== Deployment complete! ==="
echo ""
echo "Getting public URL..."
kubectl -n hooli-heard get svc frontend -o jsonpath='{.metadata.annotations.service\.beta\.kubernetes\.io/external-hostname}'
echo ""
kubectl -n hooli-heard get svc frontend
