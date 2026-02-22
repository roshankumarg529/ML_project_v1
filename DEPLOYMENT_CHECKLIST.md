# Production EKS Deployment Checklist

## Pre-Deployment

- [ ] AWS Account with appropriate IAM permissions
- [ ] Terraform installed (v1.0+)
- [ ] AWS CLI v2 configured and authenticated
- [ ] Docker image built and pushed to ECR (`ml-inference-service:latest`)
- [ ] Model files trained and included in Docker image
- [ ] GitHub Actions workflows tested and working

## Infrastructure Setup (Terraform)

- [ ] Review `infrastructure/prod.tfvars` for your environment
- [ ] Run `terraform init` in infrastructure directory
- [ ] Review `terraform plan` output before applying
- [ ] Run `terraform apply` and verify all resources created
- [ ] Verify OIDC provider ARN from Terraform output
- [ ] Note the cluster endpoint and node role ARN

## Kubernetes Tools

- [ ] kubectl installed and PATH configured
- [ ] Helm 3.x installed
- [ ] eksctl installed (optional but recommended)
- [ ] Updated kubeconfig: `aws eks update-kubeconfig --region ap-southeast-2 --name ml-inference-prod-cluster`
- [ ] Verified cluster access: `kubectl cluster-info`

## AWS Load Balancer Controller

- [ ] Added Helm repository: `helm repo add eks https://aws.github.io/eks-charts`
- [ ] Created IAM policy: AWSLoadBalancerControllerIAMPolicy
- [ ] Created ServiceAccount with IRSA in kube-system namespace
- [ ] Installed controller via Helm
- [ ] Verified controller is running: `kubectl get deployment -n kube-system aws-load-balancer-controller`

## IAM Setup for Pods (IRSA)

- [ ] Created IAM role: `ml-inference-pod-role`
- [ ] Created IAM policy: `ml-inference-pod-policy` from `infrastructure/iam-policy.json`
- [ ] Attached policy to role
- [ ] Configured trust relationship with OIDC provider for ServiceAccount: `system:serviceaccount:ml-inference:ml-inference-sa`

## Kubernetes Deployment

- [ ] Applied namespace and ConfigMap: `kubectl apply -f kubernetes/01-namespace-configmap.yaml`
- [ ] Applied Ingress and NetworkPolicy: `kubectl apply -f kubernetes/02-ingress-network-policy.yaml`
- [ ] Applied RBAC and monitoring: `kubectl apply -f kubernetes/03-rbac-monitoring.yaml`
- [ ] All pods are running: `kubectl get pods -n ml-inference`
- [ ] All pods are ready: `kubectl get pods -n ml-inference` (3/3 containers ready)

## Deployment Verification

- [ ] Get LoadBalancer URL: `kubectl get svc ml-inference-lb -n ml-inference`
- [ ] Test health endpoint: `curl http://<LB-URL>/health`
- [ ] Test prediction endpoint: `curl -X POST http://<LB-URL>/predict-single`
- [ ] Check pod logs: `kubectl logs -f deployment/ml-inference-api -n ml-inference`
- [ ] Monitor pod metrics: `kubectl top pods -n ml-inference`
- [ ] Monitor node metrics: `kubectl top nodes`

## Monitoring & Logging

- [ ] CloudWatch Container Insights enabled for cluster
- [ ] CloudWatch Log Group created: `/aws/eks/ml-inference-prod-cluster`
- [ ] Pod logs accessible via: `kubectl logs` and CloudWatch
- [ ] Cluster metrics visible in CloudWatch dashboard
- [ ] (Optional) Prometheus + Grafana installed for custom metrics
- [ ] (Optional) DataDog or New Relic agent deployed

## Auto-Scaling Verification

- [ ] HPA created and active: `kubectl get hpa -n ml-inference`
- [ ] HPA metrics available: `kubectl get hpa ml-inference-hpa -n ml-inference --watch`
- [ ] Cluster autoscaler deployed (or Karpenter)
- [ ] Tested load to verify scaling up
- [ ] Verified pods scale back down after load reduction
- [ ] Verified nodes scale based on pod requirements

## Security Verification

- [ ] RBAC roles and role bindings in place: `kubectl get roles,rolebindings -n ml-inference`
- [ ] NetworkPolicy applied: `kubectl get networkpolicy -n ml-inference`
- [ ] Pod security context enforced (non-root user)
- [ ] Pod running with read-only filesystem
- [ ] ECR image pull working correctly
- [ ] Secrets not exposed in logs or environment

## High Availability Verification

- [ ] Multiple replicas running (min 2): `kubectl get pods -n ml-inference`
- [ ] Pods spread across different nodes: `kubectl get pods -o wide -n ml-inference`
- [ ] Pod disruption budget in place: `kubectl get pdb -n ml-inference`
- [ ] Health checks configured (liveness, readiness, startup): `kubectl describe pod <pod-name> -n ml-inference`
- [ ] Rolling update strategy configured (maxSurge=1, maxUnavailable=0)
- [ ] Test by deleting a pod and verify it's recreated

## Domain Configuration (Optional)

- [ ] Domain registered (e.g., api.ml-inference.example.com)
- [ ] DNS record pointing to LoadBalancer hostname
- [ ] SSL certificate created in ACM (or self-signed for testing)
- [ ] Ingress resource configured with domain and certificate
- [ ] HTTPS redirect enabled in Ingress
- [ ] Test domain access: `curl https://api.ml-inference.example.com/health`

## Cost Optimization

- [ ] Review node instance types (t3.medium vs t3.small)
- [ ] Consider Spot instances for non-critical workloads
- [ ] Review ResourceQuota limits in namespace
- [ ] Verify autoscaling will scale down unused resources
- [ ] Review CloudWatch log retention (30 days, adjust as needed)
- [ ] Monitor AWS Cost Explorer for costs

## Backup & Disaster Recovery

- [ ] Identify persistent data (if any)
- [ ] Setup volume snapshots (if using EBS volumes)
- [ ] Document recovery procedures
- [ ] Test recovery procedures periodically
- [ ] Consider multi-region failover (if required)

## Production Hardening

- [ ] Implement Pod Security Standards (or PSP)
- [ ] Enable audit logging for Kubernetes API
- [ ] Setup VPC security group rules (restrictive ingress)
- [ ] Implement network segmentation with NetworkPolicy
- [ ] Enable AWS GuardDuty for threat detection
- [ ] Setup WAF rules for ALB (if using Ingress)
- [ ] Implement container image scanning (ECR scan)
- [ ] Regular security patches for cluster and nodes

## Documentation

- [ ] Document cluster name: `ml-inference-prod-cluster`
- [ ] Document AWS region: `ap-southeast-2`
- [ ] Document VPC CIDR: `10.0.0.0/16`
- [ ] Document IAM roles and policies
- [ ] Document LoadBalancer URL
- [ ] Document access procedures (kubectl, SSH to nodes)
- [ ] Document troubleshooting procedures
- [ ] Document runbook for common issues

## Operational Procedures

- [ ] Establish on-call rotation for cluster monitoring
- [ ] Setup alerting for cluster health (CloudWatch alarms)
- [ ] Setup alerting for pod failures (CloudWatch or Prometheus)
- [ ] Document upgrade procedures (Kubernetes, node AMI, add-ons)
- [ ] Plan monthly cluster updates
- [ ] Plan monthly node updates
- [ ] Test disaster recovery procedures
- [ ] Regular backup and restore testing

## Decommissioning (when needed)

- [ ] Delete Kubernetes namespace: `kubectl delete namespace ml-inference`
- [ ] Delete AWS Load Balancer (if created via LoadBalancer service)
- [ ] Delete IAM roles and policies
- [ ] Destroy Terraform infrastructure: `terraform destroy`
- [ ] Verify all AWS resources are deleted
- [ ] Verify ECR repository handling (keep or delete)

---

## Quick Commands Reference

```bash
# Update kubeconfig
aws eks update-kubeconfig --region ap-southeast-2 --name ml-inference-prod-cluster

# Deploy application
kubectl apply -f kubernetes/01-namespace-configmap.yaml
kubectl apply -f kubernetes/02-ingress-network-policy.yaml
kubectl apply -f kubernetes/03-rbac-monitoring.yaml

# Check deployment status
kubectl get all -n ml-inference
kubectl get hpa -n ml-inference --watch
kubectl top pods -n ml-inference

# View logs
kubectl logs -f deployment/ml-inference-api -n ml-inference
aws logs tail /aws/eks/ml-inference-prod-cluster --follow

# Get LoadBalancer URL
kubectl get svc ml-inference-lb -n ml-inference -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'

# Test API
LB_URL=$(kubectl get svc ml-inference-lb -n ml-inference -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
curl http://$LB_URL/health
curl -X POST http://$LB_URL/predict-single -H 'Content-Type: application/json' -d '{"features": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]}'

# Monitor metrics
kubectl get hpa ml-inference-hpa -n ml-inference --watch
kubectl top nodes
kubectl top pods -n ml-inference

# Cleanup
kubectl delete namespace ml-inference
cd infrastructure && terraform destroy -var-file=prod.tfvars
```

---

**Last Updated**: February 22, 2026
**Status**: Ready for deployment
