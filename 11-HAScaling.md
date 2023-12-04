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
