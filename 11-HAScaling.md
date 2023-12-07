# HA and Scaling

## Regional and Global AWS Architecture
Global:
Global Service Location adn Discovery
Content Delivery (CDN) and optimization
Global health checks and Failover

Regional:
Regional entry point
Scaling and REsilience
Application services and components

e.g. Netflix
Client -> DNS Layer R53 -> US-EAST-1 primary -> AUS secondary
- Health checks determine if primary is healthy
- CDN Layer CloudFront
- System architecture = collection of regions
- Tiers = high level groupings of functionality
  - Customers -> Web Tier (entry point for applications, abstracts customers away from infra)
  - -> Compute Tier (load balancer, EC2, etc)
  - -> Storage- EBS, EFS, S3 (S# might be cached by CF)
  - -> Caching Layer (if data not present)-> DB Tier (RDS< Aurora, DynamoDB, RedShift, etc)
  - -> App Services (SQS, SNS, etc)- email, notifcations

## Evolution of the Elastic Load Balancer (ELB)
3 Types (split between v1 (avoid/migreate) and v2 (prefer))
- Classic Load Balancer (CLB)- v1, introduced 2009
  - not really layer 7, lacking features, 1 SSL per CLB
- Application Load Balancer (ALB)- v2- HTTP/S/WebSocket
- Network Load Balancer (NLB)- v2- TCP, TLS, UDP (email, SSH, game)
- v2 = faster, cheaper, support target groups and rules

## Elastic Load Balancer Architecture
Load Balancer- distribute connection requests over backend compute

ELB Architecture
- VPC
  - AZ-A
    - Subnets
  - AZ-B
    - Subnets
- What you see as a single LB object actually represents multiple nodes
- Choose public subnet from each AZ to place LB
  - created with single DNS A record, resolves to the ELB nodes (in multiple AZs)
  - additional nodes provisioned as necessary
  - Decide if LB should be internet facing (nodes given public and private addresses) or internal (private addresses only)
- User -> ELB
  - config from "listener configuration"- accept traffic on a port and protocol and communicate with targets on a port and protocol
  - Internet-facing LB nodes can access public and private EC2 instances
- Load balancer- choose IPv4 only or dual stack (adding IPv6)
- LB reachable from public ineternet? Must be internet facing LB
- 8+ free IPs per subnet and a /27 or larger subnet to allow for scale
  - /28 doesn't leave room for LB and backend instances
- Internal LB just like internet facing, but only have private IPs for nodes
  - web server connects to app server via internal LB

Multi-Tiered Applications
  - Internet Facing LB
  - Web Instance Auto Scaling Group (ASG)
  - Internal Load Balances
  - ASG for app instances
  - DB Instances (maybe Aurora)
- Without LBs, everything tied to everything else, any instance failure = service disruption
- LBs abstract tiers from each other
  - User -> ELB node -> Web server instance -> Internal LB -> App instance -> DB
  - without LB, tiers are tighly coupled
  - LB removes coupling, allows tiers to operate independently and scale independently
  - tiers not aware of each other, only of the LB

Cross-Zone LB
  - User -> DNS Name Blog app (actually LB DNS Name), Node in each AZ, requests distrubuted equally to each AZ
    - AZ-A LB Node
    - AZ-B LB Node
    - Each node gets 100% / Number of nodes, e.g. 50% in this example
    - 4 instances in AZ-A, 1 in AZ-B
      - Node A splits connections 4 ways, Node B sends all conections to one instance
      - fix is Cross-Zone LB
  - Requests distributed among all known isntances, nodes can distribute across AZs
    - now enabled by default

Most Important ELB Architecture Points!
  - ELB is a DNS A record pointing at 1+ nodes per AZ
  - Nodes (in one subnet per AZ) can scale
  - Internet-facing means nodes have public IPv4 IPs
  - Internal is private only IPs
  - EC2 doesn't need to be public to work with a LB
    - Internet-facing can accept internet connections and balance across public AND private EC2 instances
  - Listener Configuration controls WHAT the LB does/listens to
  - 8+ free IPs per subnet, and /27 subnet to allow scaling

## Application and Network Load Balancer (ALB vs NLB)
Load Balancer Consolidation
- historically insances connect directly to LB
  - Domain name -> LB -> EC2 in auto-scaling group
  - don't scale, SNI isn't supported
  - every unique HTTP app requires its own LB
  - avoid this!
-  2 Apps -> single ELB -> Host rule for each app, 1 SSL PER rule -> Target Group -> EC2 in ASG

### Application Load Balancer (ALB)
- True Layer 7 load balancer... listens on HTTP and/or HTTPS
- No other Layer 7 protocols (SMTP, SSH, Gaming...)
- ...and NO TCP/UDP/TLS Listeners
- L7 content type, cookies, custom headers, user locaiotn, and app behavior
- HTTP HTTPS (SSL/TLS) always terminated on the ALB- no unbroken SSL
- ...a new connection is made to the application (this matter to security teams)
  - no end-to-end encryption client -> app
- ALB MUST have SSL certs if HTTPS is used
- ALBs are slower than NLB... more levels of the network stack to process
- Health checks evaluate application health at Layer 7

### ALB Rules
- Rules direct connections which arrive at a listener
- Processed in priority order
- Default Rule = catchall
- Rule Conditions: host-header, http-header, http=request-method, path-pattern, query-string, and source-ip
- Actions: forward, redirect, fixed-response, authenticate-oidc, authenticate-cognito

ALB - Rules
- IP 1.3.3.7 -> URL -> ALB -> Target Group 1 -> EC2
  - Define listen rule, source IP -> forward to alternative target
  - no option to pass through encrypted connection to instances, terminated on load balancer
  - Define rule, doggogram.io address redirects from ALB to doggogram app

### Network Load Balancer(NLB)
- Layer 4 load balancer... TCP, TLS, UDP, TCP_UDP
- No visibility or understanding of HTTP or HTTPS
- No headers, no cookies, no session stickiness
- Really really fast (millions of rps, 25% of ALB latency)
- ...SMTP, SSH, Game servers, financial apps (not http/s)
- Health checks JUST check ICMP/TCP Handshake... not app aware
- NLBs can have static IPs- useful for whitelisting
- Forward TCP to instances... *unbroken encryption*
- Used with private link to provide services to other VPCs

### ALB vs NLB
- Unbroken encryption - NLB
- Statis IP for whitelisting - NLB
- Fastest performance - NLB (millions rps)
- Protocls not HTTP/S - NLB
- Privatelink - NLB
- Otherwise - ALB

## Launch Configurations and Launch Templates
Key Concepts
- Allow you to define config of EC2 instance in advance
- AMI, Instance Type, Storage & Key pair
- Networking and Security Groups
- Userdata and IAM Role
- Both are NOT editable - defined once. LT has versions.
- LT provide newer features- including T2/T3 Unlimited, Placement Groups, Capacity Reservations, Elastic Graphics
- LT offer more utility

Launch Configuration -> Auto Scaling Groups
  - not editable... no versioning

Launch Template -> Auto Scaling Groups
  -> EC2 Instances
  - used to save time when provisioning EC2 instances from the UI/CLI

## Auto-Scaling Groups
Used with ELB and Launch templates
- Automatic Scaling and Self-Healing for EC2
- Uses Launch Templates or Configurations
- Has a Minimum, Desired, and Maximum size (e.g. 1:2:4)
- Keeps running instances at the desired capacity by provisioning or terminating instances
- Scaling policies automate based on metrics 

VPC:
- Auto Scaling Group (with launch template)
- Minimum size (1)
- Desired (2)
- Max (4)
Scaling policies automatically adjust the desired capacity between mix and max

ASG Architecture
- Define where isntances are launched
- Linked to VPC
- Attempts to keep mumber of instances in each AZ even

Scaling Policies
- Manual Scaling- manually adjust the desired capacity
- Scheduled Scaling- time based adjustment, e.g. Sales
- Dynamic Scaling
  - Simple- "CPU above 50% +1","CPU Below 50 -1"
  - Stepped Scaling- Bigger +/- based on difference (e.g. spike in load, add more instances), usually preferrable to simple
  - Target Tracking- Desired aggregate CPU = 40% ,,,ASG handles it
- Cooldown Periods (value in seconds), time to wait after scaling action before performing another

Health
- Monitos health with EC2 status checks
- Failure- terminate and create new instance in its place

ASG + Load Balancers
User -> LB -> blog -> Target Group 1 (ASG instances are automatically added to or removed from the target group)
- ASG can use the Load Balancer health checks rather than EC2 status checks- Application Awareness
  - make sure to use appropriate checks

Scaling Processes
- Launch and Terminate - Susped and Resume
- AddToLoadBalancer- add to LB on launch
- AlarmNotification- accept notification from CW
- AZRebalance- balances instances evenly across all of the AZs
- HealthCheck- instance checks on/off
- ReplaceUnhealthy- scheduled on/off
- Standby- use this for instances :InService vs Standby"

More Points...
- They are free
- Only the resources created are billed
- Use cooldowns to avoid rapid scaling
- Think about more, smaller instances- granularity
- Used with ALBs for elasticity- abstraction
- ASG defines WHEN and WHERE, LT defines WHAT

## ASG Scaling Policies
- ASGs don't NEED scaling policies- they can have none
- Manual- Min, Max, and Desired- Testing and Urgent
- Simple Scaling (e.g. add instance if CPU >40%), based on alarm state
- Step Scaling- based on size of alarm breach (better than simple)
- Target Tracking- predefined set of metrics (CPU, etowrk, ALB requests), adjusts capacity as required
- Scaling based on SQS- ApproximateNumberOfMessagesVisible, increase based on queue

Simple Scaling
- ASG 1:1:4
- Avg CPU 10%
- If ASGAverageCPUUtilization > 50% ADD 2 instances
- If ASGAverageCPUUtilization <> 50% REMOVE 2 instances
- not very flexible

Step Scaling
- 50-59% Do Nothing
- 60-69% ADD 1
- 70-79% Add 2
- 80-110% Add 3
- same for steps below 50, but Remove
- never go below min or above max

## ASG Lifecycle Hooks
- Allow you to configure custom actions on instances during ASG actions
- ...Instance launch or Instance terminate transitions
- Instances are paused within the flow... they wait
- ...until a timeout (then either Continue or Abandon)
- ...or you resume the ASG process CompleteLifecycleAction
- EventBridge or SNS Notifications

Auto Scaling Group
- Scale Out -> Pending -> InService
- Define lifecycle hook: Pending -> Pending:Wait (e.g. Load or Index data during Wait) -> Pending:Proceed -> InService
- Wait and Procedd allows for custom actions
- Scale In -> Terminating -> Terminated
- Lifecycle Hook: Terminating -> Terminating:Wait (state changes when timeout, 3600s default, expires or CompleteLifecycleAction), e.g. backups data or logs -> Terminating:Proceed

## ASG Health Checks - EC2 vs ELB
- EC2 (Default), ELB (can be enabled), and Custom
- EC2- Stopping, Stopped, Terminated, Shutting Down, or Impaired (not 2/2 status) = UNHEALTHY
- ELB- Healthy = Running and passing ELB health check
- ...can be more application aware (Layer 7)
- Custom- Instances marked healthy and unhealthy by an external system
- Health check grace period (Default 300s)- Delay before starting checks
- ...allows system launch, bootstrapping, and application start
  - don't want health checks to take effect before isntance done provisioning, botostrap, config, etc.

## SSL Offload and Session Stickiness
SSL Offload
- Bridging (default)
  - Clients -> ELB
  - Listener is configured for HTTPS, conenction is terminated on the ELB and needs a certificate for the domain name
  - LB makes second SSL connections to backend instacnes (EC2), SSL wrapper removed, create new encrypted session
  - can see HTTP traffic contents
  - certificates located on EC2 instances (may be a problem with some company security policies), a risk
- Pass-through
  - Client connects, but LB just passes connection along
  - encryption maintained between client and backend, NLB doesn't need cretificates
  - Listener is configured for TCP, no encryption or decryption happens on the NLB
  - Each instance needs to have the appropriate SSL cert installed, no cert exposure to AWS, all self-managed and secured
- Offload
  - Clients HTTPS -> ELB -> unencrypted to backend
  - Listener is configured for HTTPS, connections are terminated and then backend connections use HTTP
  - no cert or cryptographic requirements
  - data in plaintext across AWS network

Connection Stickiness
- Customer -> LB -> Backend EC2
- With no stickiness, connections are distributed across all in-service backend instances, unless application handles user state this could cause user logoffs or shopping cart losses
- User makes request, LB generates cooke called "AWSALB", duration between 1s and 7 days, user connects to the same backend instance
  - will happen until server failure or cookie expires
  - can cause uneven load on backend servers
- Use stateless service when possible, store user state externally (maybe DynamoDB)

## Seeing Session Stickiness in Action - DEMO



