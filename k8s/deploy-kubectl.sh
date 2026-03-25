#!/bin/bash
# Deploy to CKS — kubectl only (images built by GitHub Actions)
set -e

echo "=== Deploying Hooli Heard to CKS ==="
echo ""

# 1. Namespace + secrets
echo "Step 1/6: Creating namespace and secrets..."
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secret.yaml

# 2. Postgres
echo "Step 2/6: Deploying Postgres..."
kubectl apply -f k8s/postgres.yaml
echo "  Waiting for Postgres to be ready..."
kubectl -n hooli-heard wait --for=condition=ready pod -l app=postgres --timeout=120s

# 3. Backend
echo "Step 3/6: Deploying backend..."
kubectl apply -f k8s/backend.yaml
echo "  Waiting for backend to be ready..."
kubectl -n hooli-heard wait --for=condition=available deployment/backend --timeout=180s

# 4. Frontend
echo "Step 4/6: Deploying frontend..."
kubectl apply -f k8s/frontend.yaml
echo "  Waiting for frontend to be ready..."
kubectl -n hooli-heard wait --for=condition=available deployment/frontend --timeout=120s

# 5. Seed database
echo "Step 5/6: Seeding database..."
kubectl -n hooli-heard delete job seed-db --ignore-not-found
kubectl apply -f k8s/seed-job.yaml
echo "  Waiting for seed to complete..."
kubectl -n hooli-heard wait --for=condition=complete job/seed-db --timeout=120s

# 6. Get public URL
echo ""
echo "Step 6/6: Getting public URL..."
echo "=== Deployment complete! ==="
echo ""

EXTERNAL_IP=$(kubectl -n hooli-heard get svc frontend -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)

if [ -n "$EXTERNAL_IP" ]; then
  echo "Public IP: http://$EXTERNAL_IP"
fi

echo ""
kubectl -n hooli-heard get svc frontend
echo ""
kubectl -n hooli-heard get pods
