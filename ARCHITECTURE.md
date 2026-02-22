# ML Inference Service - Complete EKS Production Setup

## Executive Summary

This package contains a **production-grade Kubernetes deployment** for your ML Classification API using AWS EKS. It includes:

✅ Complete Infrastructure as Code (Terraform)  
✅ Kubernetes manifests with best practices  
✅ Auto-scaling (pods & nodes)  
✅ High availability across 2 AZs  
✅ Security hardening (RBAC, NetworkPolicy, IRSA)  
✅ Monitoring & logging integration  
✅ Cost-optimized architecture  

## What's Included

### 📁 Directory Structure

```
ML_project_v1/
├── infrastructure/              # AWS EKS Infrastructure (Terraform)
│   ├── main.tf                 # VPC, EKS, node groups, monitoring
│   ├── variables.tf            # Variable definitions
│   ├── prod.tfvars             # Production configuration
│   ├── iam-policy.json         # IAM policy for pods
│   └── outputs.tf              # (Terraform outputs)
│
├── kubernetes/                  # Kubernetes Manifests
│   ├── 01-namespace-configmap.yaml    # Deployment, HPA, PDB
│   ├── 02-ingress-network-policy.yaml # Ingress, NetworkPolicy
│   └── 03-rbac-monitoring.yaml        # RBAC, ServiceMonitor
│
├── EKS_DEPLOYMENT_GUIDE.sh      # Interactive step-by-step guide
├── EKS_README.md                # Comprehensive documentation
├── DEPLOYMENT_CHECKLIST.md      # Pre & post-deployment checklist
└── ARCHITECTURE.md              # Architecture diagrams (this file)
```

## Architecture at a Glance

```
Internet
   │
   ▼
┌──────────────────────┐
│ AWS NLB (Public)     │ ← Managed by AWS
│ Port 80 → 5000      │
└──────────────────────┘
   │
   ▼
┌──────────────────────────────────────────────────┐
│      EKS Cluster (ml-inference-prod-cluster)    │
│  ─────────────────────────────────────────────  │
│                                                  │
│  Namespace: ml-inference                        │
│  ┌──────────────────────────────────────────┐  │
│  │ Deployment: ml-inference-api             │  │
│  │ Replicas: 2-10 (HPA auto-scales)         │  │
│  │ ┌──────────────────────────────────────┐ │  │
│  │ │ Pod (Container)                      │ │  │
│  │ │ Image: ECR ML Service                │ │  │
│  │ │ Port: 5000                           │ │  │
│  │ │ CPU: 250m-1000m | Memory: 512Mi-1Gi │ │  │
│  │ │ Health checks enabled                │ │  │
│  │ └──────────────────────────────────────┘ │  │
│  │ ┌──────────────────────────────────────┐ │  │
│  │ │ Pod (Container)                      │ │  │
│  │ │ ... (more replicas)                  │ │  │
│  │ └──────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────┘  │
│                                                  │
│  Nodes (t3.medium, auto-scaled 1-4)             │
│  ┌──────────────┐    ┌──────────────┐          │
│  │   Node 1     │    │   Node 2     │          │
│  │ (AZ: ap-se-1)│    │ (AZ: ap-se-2)│          │
│  └──────────────┘    └──────────────┘          │
│                                                  │
│  Control Plane (Managed by AWS):                │
│  - Multi-AZ API servers                        │
│  - Auto-scaling etcd                           │
│  - CloudWatch Logs enabled                     │
│  - OIDC Provider for IRSA                      │
└──────────────────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────────────┐
│    AWS Services Integration                  │
│  ─────────────────────────────────────────  │
│  ✓ ECR: Image registry                      │
│  ✓ CloudWatch: Logs & Metrics               │
│  ✓ AWS Secrets Manager: Sensitive data      │
│  ✓ IAM: IRSA for pod permissions            │
│  ✓ VPC: Private subnets + NAT               │
│  ✓ Auto Scaling: Pods & Nodes               │
└──────────────────────────────────────────────┘
```

## Key Components

### 1. Terraform Infrastructure
- **VPC**: Custom VPC with public/private subnets across 2 AZs
- **EKS Control Plane**: Managed Kubernetes service (1.28)
- **Node Group**: Auto-scaling EC2 nodes (t3.medium, 1-4 nodes)
- **Security**: Security groups, NACL, OIDC provider
- **Networking**: NAT gateways, Internet gateway, route tables
- **Monitoring**: CloudWatch Container Insights enabled

**Cost Estimate**: ~$150-200/month for control plane + ~$50-100/month for 2 nodes

### 2. Kubernetes Deployment
- **Replicas**: 2-10 (auto-scales based on CPU/Memory)
- **Health Checks**: Liveness, readiness, startup probes
- **Resource Limits**: CPU 250m-1000m, Memory 512Mi-1Gi
- **Pod Anti-affinity**: Spreads pods across nodes for HA
- **Rolling Updates**: Zero-downtime deployments

### 3. Service & Ingress
- **ClusterIP Service**: Internal communication (port 5000)
- **LoadBalancer Service**: External access via AWS NLB (port 80)
- **Ingress** (Optional): ALB-based ingress for domain routing

### 4. Auto-Scaling
- **HPA** (Horizontal Pod Autoscaler):
  - Min replicas: 2
  - Max replicas: 10
  - Target CPU: 70%
  - Target Memory: 80%

- **Cluster Autoscaler** (optional):
  - Min nodes: 1
  - Max nodes: 4
  - Automatically provisions nodes when pods can't fit

### 5. High Availability
- **Multi-AZ**: Cluster spans 2 availability zones
- **Multiple Replicas**: Always at least 2 pods running
- **Pod Disruption Budget**: Ensures minimum replicas during updates
- **Health Checks**: Automatically replaces unhealthy pods
- **Rolling Updates**: Gradual replacement of pods

### 6. Security
- **RBAC**: Role-based access control for service accounts
- **NetworkPolicy**: Restricts traffic between pods
- **Pod Security**: Non-root user, read-only filesystem
- **IRSA**: Pods assume IAM roles for AWS service access
- **Resource Quotas**: Prevents resource exhaustion

### 7. Monitoring & Logging
- **CloudWatch Container Insights**: Cluster-level metrics
- **CloudWatch Logs**: Centralized logging
- **Prometheus Integration**: Custom metrics (optional)
- **Pod Metrics**: CPU and memory per pod

## Deployment Flow

```
1. Prerequisite Check
   ├─ AWS Account setup
   ├─ Tools installed (terraform, kubectl, helm)
   └─ Docker image in ECR

2. Infrastructure Setup (Terraform)
   ├─ VPC and networking
   ├─ EKS control plane
   ├─ Node groups
   └─ Monitoring and logging

3. Cluster Configuration
   ├─ Update kubeconfig
   ├─ Install AWS Load Balancer Controller
   └─ Setup IRSA for pods

4. Application Deployment
   ├─ Create namespace
   ├─ Deploy ConfigMap and Secrets
   ├─ Deploy application (Deployment + HPA)
   ├─ Configure networking (Service + Ingress)
   └─ Setup monitoring

5. Verification
   ├─ Health checks pass
   ├─ API responds to requests
   ├─ Auto-scaling works
   └─ Logs are collected

6. Production Hardening (Optional)
   ├─ Enable SSL/TLS
   ├─ Setup backup/disaster recovery
   ├─ Configure alerting
   └─ Document procedures
```

## Resource Requirements

### Compute
- **Control Plane**: Managed by AWS, included in EKS pricing
- **Node Instances**: t3.medium (2 vCPU, 4GB RAM)
  - Min: 1 node (~$0.07/hour)
  - Typical: 2 nodes (~$0.14/hour)
  - Max: 4 nodes (~$0.28/hour)

### Storage
- **Node Disk**: 50GB per node
- **Log Retention**: 30 days (adjustable)

### Network
- **Data Transfer**: Minimal (depends on traffic)
- **Load Balancer**: AWS NLB (~$0.006/hour)

## Estimated Monthly Costs

| Component | Estimate | Notes |
|-----------|----------|-------|
| EKS Control Plane | $73.00 | Fixed cost |
| EC2 Nodes (2 t3.medium) | $50.00 | ~43 hours/month |
| NLB | $4.32 | ~720 hours/month |
| Data Transfer (out) | TBD | Depends on traffic |
| **Total (Baseline)** | **~$130/month** | Without traffic costs |

**Cost Optimization Tips:**
- Use Spot instances for non-critical workloads (saves ~70%)
- Use smaller instance types (t3.small instead of t3.medium)
- Scale down nodes during off-hours
- Monitor and optimize resource requests

## Getting Started

### Quick Start (5 minutes)
1. Read `EKS_README.md` for architecture overview
2. Review `infrastructure/prod.tfvars` for your settings
3. Run through `EKS_DEPLOYMENT_GUIDE.sh` for step-by-step instructions

### Standard Deployment (30-45 minutes)
1. Setup prerequisites (tools, AWS credentials)
2. Deploy infrastructure with Terraform
3. Configure Kubernetes cluster
4. Deploy application manifests
5. Verify and test

### Full Production Setup (2-3 hours)
1. Complete standard deployment
2. Setup monitoring (Prometheus/Grafana)
3. Configure backup/disaster recovery
4. Security hardening
5. Documentation and runbooks

## Files Guide

| File | Purpose | Status |
|------|---------|--------|
| `infrastructure/main.tf` | VPC, EKS, nodes | Ready |
| `infrastructure/variables.tf` | Variable definitions | Ready |
| `infrastructure/prod.tfvars` | Production values | Ready |
| `infrastructure/iam-policy.json` | Pod IAM policy | Ready |
| `kubernetes/01-namespace-configmap.yaml` | Deployment, HPA | Ready |
| `kubernetes/02-ingress-network-policy.yaml` | Ingress, security | Ready |
| `kubernetes/03-rbac-monitoring.yaml` | RBAC, monitoring | Ready |
| `EKS_DEPLOYMENT_GUIDE.sh` | Interactive guide | Ready |
| `EKS_README.md` | Full documentation | Ready |
| `DEPLOYMENT_CHECKLIST.md` | Pre/post checklist | Ready |

## Production Best Practices Included

✅ Infrastructure as Code (Terraform)  
✅ Version-controlled configurations  
✅ Multi-AZ high availability  
✅ Auto-scaling (pods and nodes)  
✅ Health checks and probes  
✅ Rolling updates (zero-downtime)  
✅ Resource quotas and limits  
✅ RBAC and security policies  
✅ Network policies  
✅ Monitoring and logging  
✅ Container security (non-root, read-only FS)  
✅ IRSA (Kubernetes SA to AWS IAM mapping)  
✅ Pod disruption budgets  
✅ ConfigMap for configuration  
✅ Secrets management integration  

## Next Steps

1. **Review Architecture**: Read `EKS_README.md`
2. **Check Prerequisites**: Ensure all tools are installed
3. **Customize Settings**: Update `infrastructure/prod.tfvars` with your values
4. **Deploy Infrastructure**: Run Terraform commands
5. **Deploy Application**: Apply Kubernetes manifests
6. **Test**: Verify API is accessible and working
7. **Monitor**: Watch metrics and logs
8. **Optimize**: Adjust scaling policies based on traffic

## Support & Troubleshooting

### Common Issues

**Terraform error**: Check AWS credentials are configured
```bash
aws sts get-caller-identity
```

**kubectl error**: Verify kubeconfig is updated
```bash
aws eks update-kubeconfig --region ap-southeast-2 --name ml-inference-prod-cluster
```

**Pods not starting**: Check events and logs
```bash
kubectl describe pod <pod-name> -n ml-inference
kubectl logs <pod-name> -n ml-inference
```

**LoadBalancer not accessible**: Verify security groups
```bash
aws ec2 describe-security-groups --filters Name=group-name,Values=ml-inference-*
```

## References

- [AWS EKS Documentation](https://docs.aws.amazon.com/eks/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)

---

**Version**: 1.0  
**Updated**: February 22, 2026  
**Status**: Production Ready ✅

For questions or issues, refer to the deployment guide or AWS documentation.
