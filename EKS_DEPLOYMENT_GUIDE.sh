#!/bin/bash

###############################################################################
# EKS Deployment Guide for ML Inference Service (Production-Grade)
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
CLUSTER_NAME="ml-inference-prod-cluster"
REGION="ap-southeast-2"
ACCOUNT_ID="802520734572"
ECR_REPO="ml-inference-service"
NAMESPACE="ml-inference"
SERVICE_ACCOUNT="ml-inference-sa"

echo -e "${YELLOW}=== EKS Deployment Guide ===${NC}"
echo ""

# ============================================================================
# PHASE 1: Create EKS Cluster with Terraform
# ============================================================================

echo -e "${YELLOW}PHASE 1: Creating EKS Infrastructure${NC}"
echo ""
echo "Steps:"
echo "1. Install Terraform (https://www.terraform.io/downloads.html)"
echo "2. Install AWS CLI v2 (https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)"
echo "3. Configure AWS credentials:"
echo ""
echo "   aws configure sso"
echo ""
echo "   Then select your AWS account and region: ap-southeast-2"
echo ""
echo "4. Navigate to infrastructure directory:"
echo ""
echo "   cd infrastructure"
echo ""
echo "5. Initialize Terraform:"
echo ""
echo "   terraform init"
echo ""
echo "6. Review and apply the infrastructure (WILL CREATE AWS RESOURCES):"
echo ""
echo "   terraform plan -var-file=prod.tfvars"
echo "   terraform apply -var-file=prod.tfvars"
echo ""
echo "   This will create:"
echo "   - VPC with public/private subnets across 2 AZs"
echo "   - NAT Gateways for outbound traffic"
echo "   - EKS Control Plane"
echo "   - EKS Node Group (2 nodes, auto-scaling 1-4)"
echo "   - CloudWatch Log Groups"
echo "   - OIDC Provider for Kubernetes ServiceAccount to IAM role mapping"
echo ""
read -p "Press Enter after infrastructure is created..."

# ============================================================================
# PHASE 2: Configure kubectl
# ============================================================================

echo -e "${YELLOW}PHASE 2: Configuring kubectl${NC}"
echo ""
echo "1. Install kubectl (https://docs.aws.amazon.com/eks/latest/userguide/install-kubectl.html)"
echo ""
echo "2. Update kubeconfig:"
echo ""
echo "   aws eks update-kubeconfig --region $REGION --name $CLUSTER_NAME"
echo ""
echo "3. Verify cluster access:"
echo ""
echo "   kubectl cluster-info"
echo "   kubectl get nodes"
echo ""
read -p "Press Enter after kubectl is configured..."

# ============================================================================
# PHASE 3: Install AWS Load Balancer Controller
# ============================================================================

echo -e "${YELLOW}PHASE 3: Installing AWS Load Balancer Controller${NC}"
echo ""
echo "This controller enables Kubernetes Ingress resources to provision AWS ALB/NLB"
echo ""
echo "1. Add Helm repository:"
echo ""
echo "   helm repo add eks https://aws.github.io/eks-charts"
echo "   helm repo update"
echo ""
echo "2. Create IAM policy:"
echo ""
echo "   curl -o /tmp/iam_policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.6.2/docs/install/iam_policy.json"
echo ""
echo "   aws iam create-policy \\"
echo "     --policy-name AWSLoadBalancerControllerIAMPolicy \\"
echo "     --policy-document file:///tmp/iam_policy.json"
echo ""
echo "3. Create ServiceAccount with IAM role:"
echo ""
echo "   eksctl create iamserviceaccount \\"
echo "     --cluster=$CLUSTER_NAME \\"
echo "     --namespace=kube-system \\"
echo "     --name=aws-load-balancer-controller \\"
echo "     --attach-policy-arn=arn:aws:iam::$ACCOUNT_ID:policy/AWSLoadBalancerControllerIAMPolicy \\"
echo "     --approve"
echo ""
echo "4. Install the controller:"
echo ""
echo "   helm install aws-load-balancer-controller eks/aws-load-balancer-controller \\"
echo "     -n kube-system \\"
echo "     --set clusterName=$CLUSTER_NAME"
echo ""
echo "5. Verify installation:"
echo ""
echo "   kubectl get deployment -n kube-system aws-load-balancer-controller"
echo ""
read -p "Press Enter after AWS Load Balancer Controller is installed..."

# ============================================================================
# PHASE 4: Create IAM Role for Pod (IRSA)
# ============================================================================

echo -e "${YELLOW}PHASE 4: Setting Up IRSA (IAM Roles for Service Accounts)${NC}"
echo ""
echo "This allows the Kubernetes ServiceAccount to assume an IAM role"
echo ""
echo "1. Get the OIDC provider URL from Terraform output:"
echo ""
echo "   terraform output oidc_provider_arn"
echo ""
echo "2. Create IAM role and attach policy:"
echo ""
echo "   aws iam create-role --role-name ml-inference-pod-role \\"
echo "     --assume-role-policy-document='{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Federated\":\"arn:aws:iam::$ACCOUNT_ID:oidc-provider/oidc.eks.$REGION.amazonaws.com/id/YOUR_OIDC_ID\"},\"Action\":\"sts:AssumeRoleWithWebIdentity\",\"Condition\":{\"StringEquals\":{\"oidc.eks.$REGION.amazonaws.com/id/YOUR_OIDC_ID:sub\":\"system:serviceaccount:$NAMESPACE:$SERVICE_ACCOUNT\"}}}]}'"
echo ""
echo "3. Attach the policy from infrastructure/iam-policy.json:"
echo ""
echo "   aws iam create-policy --policy-name ml-inference-pod-policy \\"
echo "     --policy-document file://iam-policy.json"
echo ""
echo "   aws iam attach-role-policy \\"
echo "     --role-name ml-inference-pod-role \\"
echo "     --policy-arn arn:aws:iam::$ACCOUNT_ID:policy/ml-inference-pod-policy"
echo ""
read -p "Press Enter after IRSA is configured..."

# ============================================================================
# PHASE 5: Deploy ML Inference Service
# ============================================================================

echo -e "${YELLOW}PHASE 5: Deploying ML Inference Service${NC}"
echo ""
echo "1. Deploy Kubernetes manifests:"
echo ""
echo "   kubectl apply -f kubernetes/01-namespace-configmap.yaml"
echo "   kubectl apply -f kubernetes/02-ingress-network-policy.yaml"
echo "   kubectl apply -f kubernetes/03-rbac-monitoring.yaml"
echo ""
echo "2. Wait for deployment to be ready:"
echo ""
echo "   kubectl wait --for=condition=available --timeout=300s \\"
echo "     deployment/ml-inference-api -n $NAMESPACE"
echo ""
echo "3. Check pod status:"
echo ""
echo "   kubectl get pods -n $NAMESPACE"
echo "   kubectl logs -f deployment/ml-inference-api -n $NAMESPACE"
echo ""
echo "4. Get the LoadBalancer URL:"
echo ""
echo "   kubectl get svc ml-inference-lb -n $NAMESPACE"
echo ""
echo "5. Test the API:"
echo ""
echo "   LB_URL=\$(kubectl get svc ml-inference-lb -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')"
echo "   curl http://\$LB_URL/health"
echo "   curl -X POST http://\$LB_URL/predict-single \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"features\": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]}'"
echo ""
read -p "Press Enter after deployment is complete..."

# ============================================================================
# PHASE 6: Monitoring and Logging
# ============================================================================

echo -e "${YELLOW}PHASE 6: Monitoring and Logging${NC}"
echo ""
echo "1. View cluster logs in CloudWatch:"
echo ""
echo "   aws logs describe-log-groups --region $REGION"
echo "   aws logs tail /aws/eks/$CLUSTER_NAME --region $REGION --follow"
echo ""
echo "2. View pod logs:"
echo ""
echo "   kubectl logs -f deployment/ml-inference-api -n $NAMESPACE --all-containers=true"
echo ""
echo "3. View pod metrics:"
echo ""
echo "   kubectl top nodes"
echo "   kubectl top pods -n $NAMESPACE"
echo ""
echo "4. Optional: Install Prometheus & Grafana for advanced monitoring"
echo ""
echo "   helm repo add prometheus-community https://prometheus-community.github.io/helm-charts"
echo "   helm install prometheus prometheus-community/kube-prometheus-stack \\"
echo "     --namespace monitoring --create-namespace"
echo ""
echo "5. Port-forward to Grafana:"
echo ""
echo "   kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80"
echo "   Open: http://localhost:3000"
echo ""

# ============================================================================
# PHASE 7: Auto-scaling and High Availability
# ============================================================================

echo -e "${YELLOW}PHASE 7: Auto-scaling Verification${NC}"
echo ""
echo "1. View HPA status:"
echo ""
echo "   kubectl get hpa -n $NAMESPACE"
echo ""
echo "2. Monitor scaling in real-time:"
echo ""
echo "   kubectl get hpa -n $NAMESPACE --watch"
echo ""
echo "3. Simulate load (optional):"
echo ""
echo "   kubectl run -it --rm debug --image=busybox -- sh"
echo "   # Inside the container:"
echo "   while true; do wget -q -O- http://ml-inference-service:5000/health; done"
echo ""
echo "4. Watch pods scale up:"
echo ""
echo "   kubectl get pods -n $NAMESPACE --watch"
echo ""

# ============================================================================
# PHASE 8: Production Best Practices
# ============================================================================

echo -e "${YELLOW}PHASE 8: Production Best Practices${NC}"
echo ""
echo "✓ Enable autoscaling for nodes:"
echo "  - Cluster Autoscaler or Karpenter"
echo ""
echo "✓ Set up cost optimization:"
echo "  - Use Spot instances for non-critical workloads"
echo "  - Set resource quotas per namespace"
echo ""
echo "✓ Implement security:"
echo "  - Pod Security Policies or Pod Security Standards"
echo "  - Network Policies (already configured)"
echo "  - RBAC (already configured)"
echo "  - Regular security audits"
echo ""
echo "✓ Enable high availability:"
echo "  - Multi-AZ deployment (already configured)"
echo "  - Pod disruption budgets (already configured)"
echo "  - Multiple replicas (already configured)"
echo ""
echo "✓ Set up CI/CD:"
echo "  - GitHub Actions already configured to build and push to ECR"
echo "  - Add ArgoCD or Flux for GitOps deployments"
echo ""
echo "✓ Monitoring and alerting:"
echo "  - CloudWatch alarms for cluster health"
echo "  - Prometheus + AlertManager for detailed metrics"
echo "  - DataDog or New Relic integration"
echo ""
echo "✓ Backup and disaster recovery:"
echo "  - Regular snapshots of persistent data"
echo "  - Multi-region failover (optional)"
echo ""

# ============================================================================
# CLEANUP (if needed)
# ============================================================================

echo -e "${YELLOW}CLEANUP (when done):${NC}"
echo ""
echo "To destroy all resources and avoid ongoing costs:"
echo ""
echo "1. Delete Kubernetes resources:"
echo ""
echo "   kubectl delete namespace $NAMESPACE"
echo ""
echo "2. Destroy infrastructure:"
echo ""
echo "   cd infrastructure"
echo "   terraform destroy -var-file=prod.tfvars"
echo ""

echo -e "${GREEN}=== Deployment Guide Complete ===${NC}"
