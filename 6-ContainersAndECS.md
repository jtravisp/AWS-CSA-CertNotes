# Containers and ECS

## Introduction to Containers

### Virtualization Problems
AWS EC2 Host -> AWS Hypervisor (NITRO) -> EC2 Instances (e.g. 6 VMs, 6 Apps)
    - OS can take up 60-70% of disk and much of available memory
    - Likely that many OS are the same, this is duplication! waste of resources

### Containerization
Host Hardware -> Host OS -> Container Engine -> App #1/Runtime Env elements (libraries/dependencies)
- Container runs as a process within host OS, isolated from other processes
- Inside process, like an isolated OS
- Looks like virtualizaiton architecture, but containers much lighter (can run many more on same hardware!)

### Image Anatomy
EC2 Instance - running copy of EBS volumes in virtualized env.
Container- Docker Image
    - Docker File - creates image, each step creates FS layers
    - Images are created from a base image or scratch
    - 1st line is image of distro
    - 2nd line is software
    - Next line- create another file system layer

```
FROM centos:7
MAINTAINER The CentOS Project <cloud-ops@centos.org>
LABEL ...

RUN yum -y --setopt=tsflags=nodocs update && \
    yum -y --setopt=tsflags=nodocs install httpd && \
    yum clean all

EXPOSE 80

ADD run-httpd.sh /run-httpd.sh
RUN chmod -v +x /run-httpd.sh

CMD ["/run-httpd.sh"]
```

Docker image used to create Docker container
- Container has additional read/write file system layer (Docker image is read only)
- Anything that happens in the container is stored on R/W Layer
- Can use same image to create multiple containers
  - Layers- OS/App/Customization (all read only)
  - R/W layer separate/different for each container
- Container registry- Docker Hub is popular
  - registry of container images
  - Dockerfile -> Container image -> Container Registry (e.g. Docker Hub) -> Docker hosts
  - Download or upload your own

Docker is just one type of container, but some use the terms interchangably

### Key Concepts
Dockerfiles are used to build images
Portable - self-contained, always run as expected (libraries are all in container, runs same everywhere)
Lightweight - parent OS used, FS layers are shared (image is read only)
Only run the application and environment it needs (not full OS), use little memory, start/stop fast
Much of same isolation as VMs
Ports are "exposed" to the host and beyond
Application stacks can be multi-container

## Creating a Docker Image - DEMO
Create a docker image containing the 'container of cats' application.
We will install the docker engine on an EC2 Instance and use this to create the image.
To test the image we will 'RUN' the image, creating a docker container and once tested, upload the image to dockerhub.

```
# Install Docker Engine on EC2 Instance
sudo dnf install docker
sudo service docker start
sudo usermod -a -G docker ec2-user

LOGOUT and login

sudo su - ec2-user

# Build Docker Image
cd container
docker build -t containerofcats .
docker images --filter reference=containerofcats

# Run Container from Image
docker run -t -i -p 80:80 containerofcats

# Upload Container to Dockerhub (optional)
docker login --username=YOUR_USER
docker images
docker tag IMAGEID YOUR_USER/containerofcats
docker push YOUR_USER/containerofcats:latest
```

Dockerfile:
```
FROM redhat/ubi8

LABEL maintainer="Animals4life"

RUN yum -y install httpd

COPY index.html /var/www/html/

COPY containerandcat*.jpg /var/www/html/

ENTRYPOINT ["/usr/sbin/httpd", "-D", "FOREGROUND"]

EXPOSE 80
```

## ECS - Concepts
Managed container based compute service: ECS takes away overhead of running your own container host
Uses clusters:
1. EC2 Mode- EC2 instances as container hosts
2. Fargate Mode- Serverless, AWS handles host

Cluter- where containers run from
- ECS Cluster
- Container images come from registry (DockerHub or ECR:Elastic Container Registry)
- *Container Definition*
  - where is container, which port
  - just info about single container
- *Task Definition*- self-contained application
  - 1 or more containers
  - represents application as whole, stores all needed Container Definitions
  - resources, compatability (EC2 v. Fargate), *Task IAM Role* (temp credentials)
  - doesn't scale on its own, isn't HA
- ECS Service
  - *Service Definition* - defines how task will run
  - level of scalability and HA
  - not needed for single copy of task, it's a "service wrapper" for scalability and HA

### Key ECS Concepts
Container Definition - Image and Ports
Task Definition - Security (Task Role), Container(s), Resources
Task Role - IAM Role which TASK assumes (and any running containers)
Service - How many copies, HA, Restarts

## ECS - Cluster Mode
ECS is capable of running in EC2 mode or Fargate mode
High level in both modes: *Scheduling and Orchestration, Cluster Manager, Placement Engine*

*EC2 mode* deploys EC2 instances into your AWS account which can be used to deploy tasks and services.
    - With EC2 mode you pay for the EC2 instances regardless of container usage
    - ECS Cluster: created inside VPC (benefits from multiple AZ in VPC)
      - Specify initial size, handled by Auto Scaling Group (ASG)
      - Uses container registries (where images stored)= DockerHub or ECR -> Task and Services -> Instances in AZs
      - You manage capacity of cluster, can use EC2 spot pricing

*Fargate mode* uses shared AWS infrastructure, and ENI's (elastic network interfaces) which are injected into your VPC
    - You pay only for container resources used while they are running.
    - Don't maange EC2 instances, "serverless"
    - Same surrounding technology, still use registries, task/service definitions
    - Fargate Shared Infrastructure platform (no visibility of other customers)
    - still uses VPC with AZs
      - Tasks are injected into VPC with ENI
      - Can be accessed from within that VPC or publicly (if configured)
    - No management of hosts

### Exam - EC2 vs ECS (EC2) vs Fargate
EC2 v ECS - using containers? Use ECS.
EC2 Mode- Large workload and price conscious (if you can manage admin overhead)
Fargate- Large workload and overhead conscious
Fargate- Small/Burst workloads
Fargate- Bath/Periodic workloads

## Deploying container using Fargate - DEMO
Create a Fargate Cluster, create a task and container definition and deploy the world renowned 'container of cats' Application from Dockerhub into Fargate.

## Elastic Container Registry (ECR)
Managed container image registry service
Like DockerHub but for AWS
Each AWS account has a public and private registry
    - Each registry can have many repositories
    - Each repo can contain many images
Images can have several tags
Public = public R/O... R/W requires permissions
Private = premission required for an R/o or R/W

Integrated with IAM - Permissions
Image scanning- Basic and Enhanced (using Insspector product)
Near real-time metrics -> CW (auth, push, pull)
API Actions -> CloudTrail
Event -> EventBridge
Replication - Cross-region and Cross-account

## Kubernetes 101
Open source conatiner orchestration - run containers in a reliable and scalable way
Cloud agnostic
K8 Cluster:
    - HA cluster of compute resources which are organized to work as 1 unit
  - Starts with *Cluster Conrol Plane* - scheduling, applications, scalign, and deploying
  - *Cluster Nodes* - VM or physical server which functions as "worker" in the cluster, actually run conatinerized apps
    - on each node: "containerd" or Docker software for handling container operations - Container Runtime
    - kubelet - agent to interact with cluster control plane using:
      - Kubernetes API - communication between control plane and kubelet agent

Conrol Plane
- *kube-apiserver* - the front end for the control plane
- *etcd* provides HA key value store, used as main backing store for the cluster
- *kube-scheduler* IDs and pods within cluster with no assigned node and assign node based on resource requirements, deadlines, affinity/anti-affinity, data localitym and any contraints
- *cloud-controller-manager* - provides cloud-specific contorl logic (OPTIONAL) - cloud provider APIs (AWS/Azure/GCP)
- *kube-controller-manager* cluster controller processes:
  - Node Controller- monitoring and responding to node outages
  - Job Controller- one-off tasks (jobs) -> PODS
  - Endpoint Controller- populates endpoints (Services <-> PODS)
  - Service Account and Token Controllers - Accounts/API Tokens

Cluster Node
- usually many
- Inside a Node: *Pods* are the smallest unit of computing, shared storage and networking "one-container-one-pod" is commong
  - Pods are nonpermanent, created to do a job, then disposed of
- *kube-proxy* runs on every node- coordinates networking with the control plane, helps implement "services" and configure rules allowing comms with pods from inside or outside the cluster

### Summary
Cluseter - deployment of Kubernetes, management, orchestration...
Node - resources, pods placed on Nodes to run
Pod - 1+ containers, smallest unit in kubernetes, often 1container-1pod
Service - abstraction, service running on 1 or more pods
Job - ad-hoc, creates one of more pods until completion
Ingress - exposes a way into a service (Ingress -> Routing -> Service -> 1+ Pods)
Ingress Controller - used to provide ingress (e.g. AWS LB Controller uses ALB/NLB)
Storage is ephemeral (pod moved loses storage)
Persistent Storage (PV) - volume whose lifesycle lives beyond any 1 pod using it

## Elastic Kubernetes Service (EKS)
Fully-managed Kubernetes implementation that simplifies the process of building, securing, operating, and maintaining Kubernetes clusters on AWS.
Open source and cloud agnostic
Same as K8 anywhere else, just optimized for AWS
Control plane scales and runs on multiple AZs
Integrates with AWS services - ECR, ELB, IAM, VPC
EKS Cluster = EKS Control Plane and EKS Nodes
*etcd* distributed across multiple AZs
Nodes- Self Managed, Managed node groups, or Fargate pods (no configuration or scaling, define Fargate profiles similar to ECS Fargate)
    - Windows, GPU, Inferentia, Bottlerocket, Outposts, Local zones, etc. - check node type needed!
Storage Providers for persistent storage - includes EBS, EFX, FSx Lustre, etc.

2 VPCs
 - 1- AWS Managed VPC (control plane)
   - EKS admin via public endpoint
 - 2- Customer VPC (worker nodes)
 - Control Plane ENIs injected into Customer VPC
