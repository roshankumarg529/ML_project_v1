# Production Environment Override
environment = "prod"
project_name = "ml-inference"
cluster_name = "ml-inference-prod-cluster"
kubernetes_version = "1.28"

# Network Configuration
vpc_cidr = "10.0.0.0/16"
public_subnet_cidrs = ["10.0.1.0/24", "10.0.2.0/24"]
private_subnet_cidrs = ["10.0.10.0/24", "10.0.11.0/24"]

# Node Configuration
instance_types = ["t3.medium"]
desired_size = 2
min_size = 1
max_size = 4
disk_size = 50

# Logging
log_retention_days = 30
