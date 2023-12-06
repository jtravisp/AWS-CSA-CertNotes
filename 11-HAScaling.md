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


