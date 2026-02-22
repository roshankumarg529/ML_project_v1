# Production-Grade EKS Deployment for ML Inference Service

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    AWS Account (ap-southeast-2)              │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │               VPC (10.0.0.0/16)                      │   │
│  │                                                       │   │
│  │  ┌─ Public Subnets ─┐         ┌─ Private Subnets ─┐ │   │
│  │  │ (10.0.1-2.0/24)  │         │ (10.0.10-11.0/24)│ │   │
│  │  │                   │         │                   │ │   │
│  │  │  NAT Gateway     │         │   EKS Nodes (t3) │ │   │
│  │  │  IGW             │         │   - ML API Pod    │ │   │
│  │  │                   │         │   - Replicas: 2-10
│  │  └───────────────────┘         └───────────────────┘ │   │
│  │                                                       │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │      EKS Control Plane (Managed)           │    │   │
│  │  │  - Multi-AZ deployment                     │    │   │
│  │  │  - Auto-scaling control plane              │    │   │
│  │  │  - CloudWatch Container Insights enabled   │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              AWS Services                           │   │
│  │  - ECR (ml-inference-service)                       │   │
│  │  - CloudWatch Logs & Metrics                        │   │
│  │  - AWS Secrets Manager                             │   │
│  │  - IAM OIDC Provider (IRSA)                         │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘

External Traffic
       │
       ▼
┌─────────────────────────┐
│   AWS NLB (Public)      │ ← Service Type: LoadBalancer
│   :80 → :5000          │
└─────────────────────────┘
       │
       ▼
┌─────────────────────────┐
│  Kubernetes Ingress     │ (Optional, uses ALB Controller)
│  api.example.com        │
└─────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│  ML Inference Service                       │
│  Namespace: ml-inference                    │
│  Deployment: ml-inference-api               │
│  Replicas: 2-10 (HPA based on CPU/Memory)  │
│  Service: ml-inference-service (ClusterIP) │
│  Service: ml-inference-lb (LoadBalancer)   │
└─────────────────────────────────────────────┘
```

## Directory Structure

```
ML_project_v1/
├── infrastructure/                 # Terraform IaC for EKS
│   ├── main.tf                    # VPC, EKS cluster, node groups
│   ├── variables.tf               # Variable definitions
│   ├── prod.tfvars                # Production values
│   ├── iam-policy.json            # IAM policy for pods
│   └── outputs.tf                 # (will be added for outputs)
├── kubernetes/                     # Kubernetes manifests
│   ├── 01-namespace-configmap.yaml   # Namespace, ConfigMap, Deployment, HPA
│   ├── 02-ingress-network-policy.yaml # Ingress, NetworkPolicy, ResourceQuota
│   └── 03-rbac-monitoring.yaml        # RBAC, ServiceMonitor
├── EKS_DEPLOYMENT_GUIDE.sh         # Step-by-step deployment guide
└── README.md                        # This file
```

## Key Features - Production Grade

### 1. **Infrastructure as Code (Terraform)**
- Complete VPC setup with public/private subnets across 2 AZs
- EKS Control Plane with auto-scaling
- Auto-scaling node groups (min: 1, max: 4)
- CloudWatch Container Insights integration
- OIDC Provider for Kubernetes ServiceAccount to IAM role mapping (IRSA)
- NAT Gateways for private subnet egress

### 2. **Kubernetes Deployment**
- **Multi-replica deployment** (2 replicas minimum for HA)
- **Horizontal Pod Autoscaler (HPA)**: Scales 2-10 pods based on CPU (70%) and Memory (80%)
- **Pod Anti-affinity**: Spreads pods across nodes
- **Health checks**: 
  - Liveness probe (restarts unhealthy pods)
  - Readiness probe (removes from load balancer if unhealthy)
  - Startup probe (gives container time to initialize)
- **Resource requests/limits**: CPU 250m/1000m, Memory 512Mi/1Gi
- **Security context**: Non-root user, read-only filesystem, no privilege escalation

### 3. **Networking**
- **Service**: ClusterIP for internal communication (port 5000)
- **LoadBalancer**: AWS Network Load Balancer for external access (port 80)
- **Ingress** (optional): ALB-based ingress for domain-based routing
- **NetworkPolicy**: Restricts ingress/egress traffic (production security)

### 4. **Configuration & Secrets**
- **ConfigMap**: Application configuration (RANDOM_STATE, N_ESTIMATORS, etc.)
- **Secrets**: Sensitive data (database URLs, API keys)
- **IRSA**: Pod assumes IAM role for AWS service access

### 5. **High Availability**
- **Multi-AZ**: Cluster spans 2 availability zones
- **Pod Disruption Budget**: Ensures minimum replicas during maintenance
- **Rolling updates**: Zero-downtime deployments
- **Node auto-scaling**: Automatically scales nodes based on pod requirements

### 6. **Monitoring & Logging**
- **CloudWatch Container Insights**: Monitor cluster and pod metrics
- **CloudWatch Logs**: Centralized logging for cluster components
- **ServiceMonitor**: Prometheus integration for detailed metrics
- **Pod-level metrics**: CPU and memory tracking

### 7. **Security**
- **RBAC**: Role-based access control for ServiceAccounts
- **NetworkPolicy**: Network segmentation and traffic control
- **Pod Security**: Non-root execution, read-only filesystem
- **Least privilege**: Minimal IAM permissions via IRSA

### 8. **Resource Management**
- **ResourceQuota**: Limits namespace resource usage (4 CPU, 4Gi memory)
- **LimitRange**: Enforces container resource limits
- **HPA**: Auto-scales pods based on demand
- **Cluster autoscaler**: Scales nodes automatically

## Prerequisites

- AWS Account with sufficient permissions
- Terraform >= 1.0
- AWS CLI v2 configured with credentials
- kubectl installed
- Helm 3.x (for AWS Load Balancer Controller)
- eksctl (optional, simplifies IAM setup)

## Deployment Steps

### Phase 1: Create Infrastructure
```bash
cd infrastructure
terraform init
terraform plan -var-file=prod.tfvars
terraform apply -var-file=prod.tfvars
```

### Phase 2: Configure kubectl
```bash
aws eks update-kubeconfig --region ap-southeast-2 --name ml-inference-prod-cluster
kubectl cluster-info
```

### Phase 3: Install AWS Load Balancer Controller
```bash
helm repo add eks https://aws.github.io/eks-charts
helm repo update
# (Follow guide for IAM policy and IRSA setup)
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system --set clusterName=ml-inference-prod-cluster
```

### Phase 4: Setup IRSA
```bash
# Create IAM role and attach policy
aws iam create-role --role-name ml-inference-pod-role ...
aws iam attach-role-policy --role-name ml-inference-pod-role \
  --policy-arn arn:aws:iam::802520734572:policy/ml-inference-pod-policy
```

### Phase 5: Deploy Application
```bash
kubectl apply -f kubernetes/01-namespace-configmap.yaml
kubectl apply -f kubernetes/02-ingress-network-policy.yaml
kubectl apply -f kubernetes/03-rbac-monitoring.yaml

# Wait for deployment
kubectl wait --for=condition=available --timeout=300s \
  deployment/ml-inference-api -n ml-inference
```

### Phase 6: Verify Deployment
```bash
kubectl get pods -n ml-inference
kubectl get svc -n ml-inference
kubectl logs -f deployment/ml-inference-api -n ml-inference

# Get LoadBalancer URL
kubectl get svc ml-inference-lb -n ml-inference -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'

# Test the API
curl http://<LoadBalancer-URL>/health
curl -X POST http://<LoadBalancer-URL>/predict-single \
  -H 'Content-Type: application/json' \
  -d '{"features": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]}'
```

## Monitoring & Observability

### CloudWatch Container Insights
```bash
# View cluster metrics
aws cloudwatch get-metric-statistics \
  --namespace ContainerInsights \
  --metric-name PodCPU \
  --dimensions Name=ClusterName,Value=ml-inference-prod-cluster \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 300 \
  --statistics Average
```

### Pod Metrics
```bash
kubectl top pods -n ml-inference
kubectl top nodes
```

### Logs
```bash
kubectl logs -f deployment/ml-inference-api -n ml-inference

# Stream CloudWatch logs
aws logs tail /aws/eks/ml-inference-prod-cluster --follow
```

## Auto-Scaling

### Pod Horizontal Scaling
- Configured via HPA in `01-namespace-configmap.yaml`
- Scales 2-10 replicas based on CPU (70%) and Memory (80%)
- Scale-up: Immediate (0s stabilization)
- Scale-down: 5 minutes (300s stabilization)

### Node Auto-Scaling
- Install Cluster Autoscaler or Karpenter
- Automatically scales nodes based on pod requirements
- Respects min (1) and max (4) node limits

## Cost Optimization

1. **Use Spot Instances**: Configure node group with spot instances (saves ~70%)
2. **Adjust node size**: Currently t3.medium, can use t3.small for lower cost
3. **Resource quotas**: Prevents resource waste via ResourceQuota limits
4. **Scale down**: Cluster auto-scales down when demand decreases

## High Availability Checklist

✅ Multi-AZ deployment (2 AZs)  
✅ Multiple pod replicas (2-10)  
✅ Pod disruption budget (min 1 replica)  
✅ Health checks (liveness, readiness, startup)  
✅ Rolling updates (zero-downtime)  
✅ Node auto-scaling (1-4 nodes)  
✅ Pod anti-affinity (spreads across nodes)  
✅ Network policies (traffic control)  

## Security Checklist

✅ RBAC (least privilege)  
✅ IRSA (IAM roles for ServiceAccounts)  
✅ NetworkPolicy (network segmentation)  
✅ Pod security context (non-root, read-only FS)  
✅ Resource quotas (prevent DoS)  
✅ Secrets management (AWS Secrets Manager integration)  
✅ Container image from ECR (private registry)  
✅ CloudWatch Container Insights (monitoring)  

## Cleanup

To avoid ongoing AWS charges:

```bash
kubectl delete namespace ml-inference

cd infrastructure
terraform destroy -var-file=prod.tfvars
```

## Troubleshooting

### Pod not starting
```bash
kubectl describe pod <pod-name> -n ml-inference
kubectl logs <pod-name> -n ml-inference --previous
```

### LoadBalancer not accessible
```bash
kubectl get svc ml-inference-lb -n ml-inference
aws ec2 describe-security-groups --filters Name=group-name,Values=ml-inference-*
```

### Node issues
```bash
kubectl describe nodes
kubectl get events -n ml-inference --sort-by='.lastTimestamp'
```

## Additional Resources

- [EKS Best Practices Guide](https://aws.github.io/aws-eks-best-practices/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS Load Balancer Controller](https://kubernetes-sigs.github.io/aws-load-balancer-controller/)

## Contact & Support

For issues or questions about this EKS setup, refer to the deployment guide or AWS documentation.
