# Virtual Private Cloud (VPC) Basics

## VPC Sizing and Structure

### Starting Points for Design:
What size should VPC be?

Are there any networks we can't use? 
- Be mindful of other VPCs, cloud, on-prem, partners and vendors

Try to predict the future....

VPC Structure - Tiers and Resiliency (Availability) Zones

### Animals4Life example org
3 Major Offices + Head Office
Field works in range of locations
Current:
    On-premise 192.168.10.0/24 (192.168.10.0 -> 192.168.10.255)
    AWS Pilot 10.0.0.0/16
    Azure Pilot 172.31.0.0/16
    - have to avoid those ranges
    - Azure is using the default AWS range!
    Also offices and Google (10.128.0.0/9)

Considerations:
- VPC min /28 (16 IP), max /16 (65536 IPs)
- Personal pref for the 10.x/y/z range
- Avoid common ranges (to avoid future issues)
- Reserve 2+ networks per region being used per account
- 3 US, Europe, Australia (5) x2 - Assume 4 accounts
  - Total 40 ranges (ideally)

More Considerations:
APC Sizing
    - Micro /24
    - XL /16
- How many subnets?
  - VPC services run in subnets (located in 1 AZ)
  - Start with 3 as default AZ + 1 spare
    - AZ-A, AZ-B, AZ-C, Future
  - 4 Tiers
    - Web, App, DB, Spare (/20 subnet in each)
  - Same subnets in each AZ
  - 4 AZs x 4 Tiers = 16 subnets

Proposal
- Plan on growth
- Use the 10.16 -> 10.127 (avoiding Google, 10.1-10.15 avoid, 10.128+ is Google)
- 10.16, 10.32, 10.48, 10.64, 10.80 - each AWS account has 1/4th
- Plan IP address ranges on any new project
- /16 per VPC = 3 AZ (+spare), 3 Tiers (+spare) - 16 subnets
- /16 split into 16 subnets = /20 per subnet (4091 IPs)

## Custom VPCs (Theory and Demo)
- VPC 10.16.0.0/16
  - inside- space for 4 tiers
  - each tier- DB, App, Web
  - Bastion host- 1 way to connect to VPC (bad, not best practice)
    - later- more secure alternatives
  - see PDF design

Regional Service - All AZs in the region
- Isolated network
- Nothing IN or OUT without explicit config
- Flexible config - simple or multi-tier
- Hybrid networking- other cloud and on-prem
- Default or Dedicated Tenancy (cost premium)

IPv4 private CIDR blocks and Public IPs
1 Primary Private IPv4 CIDR block
  - Min /28 (16 IP) Max /16 (65,536 IP)
  - optional secondary IPv4 blocks
  - optional single *assigned* IPv6 /56 CIDR block (should start looking at applying as default)

DNS in VPC
- provided by R53
- *Base IP +2* address
- setting: enableDnsHostnames - give instances DNS names
- setting: enableDnsSupport - enables DNS resolution in VPC

### Demo
Create VPC Only (other components later)
IPv4 CIDR - 10.16.0.0/16
IPv6 CIDR (Network border group) - 2600:1f18:324b:1500::/56 (us-east-1)

## VPC Subnets
Subnets - where services run inside VPCs

Create internal structure using subnets - DB, App, Web
- subnets start prviate, must be congigured for public

Subnets:
  - AZ resilient
  - Subnetwork of a VPC - within a particular AZ
  - Highly Available- put compnents in different AZs/Subnets
    - 1 Subnet => 1 AZ, 1 AZ => 0+ Subnets
  - IPv4 CIDR is a subset up the VPC CIDR
  - Cannot overlap with other subnets
  - Optional IPv6 CIDR (/64 subset of the /56 VPC - space for 256)
  - Subnets can communicate with other subnets in the VPC
  
Subnet IP Addressing
  - Reserved IP addresses (5 in total)
    - 10.16.16.0/20 (10.16.16.0 => 10.16.31.255)
      - Network Address (10.16.16.0)
      - Network +1 (10.16.16.1) - VPC Router
      - Network +2 (10.16.16.2) - Reserved for DNS
      - Network +3 (10.16.16.3) - Reserve for future use
      - Broadcast Address (10.16.31.255) - last address in subnet
  - Instance
    - DHCP Options Set (1 applied at one time, flows to subnets)
    - Can define per subnet:
      - Auto Assign Public IPv4 (in addition to private address)
      - Auto Assign IPv6

### Subnet Demo
Configure each subnet one by one
https://www.site24x7.com/tools/ipv4-subnetcalculator.html

NAME CIDR AZ CustomIPv6Value

sn-reserved-A 10.16.0.0/20 AZA IPv6 00
sn-db-A 10.16.16.0/20 AZA IPv6 01
sn-app-A 10.16.32.0/20 AZA IPv6 02
sn-web-A 10.16.48.0/20 AZA IPv6 03

sn-reserved-B 10.16.64.0/20 AZB IPv6 04
sn-db-B 10.16.80.0/20 AZB IPv6 05
sn-app-B 10.16.96.0/20 AZB IPv6 06
sn-web-B 10.16.112.0/20 AZB IPv6 07

sn-reserved-C 10.16.128.0/20 AZC IPv6 08
sn-db-C 10.16.144.0/20 AZC IPv6 09
sn-app-C 10.16.160.0/20 AZC IPv6 0A
sn-web-C 10.16.176.0/20 AZC IPv6 0B

Remember to enable auto assign ipv6 on every subnet you create.

## VPC Routing and Internet Gateway & Bastion Hosts
Data exit and enter setup

VPC Router- every VPC has a VPC router - highly available
- In every subnet- Network+1 address
- Routes traffic between subnets
- Controlled by route tables -  each subnet has one, defines what data does when it leaves
- A VPC has a Main route table - subnet default (custom table will disassociate the Main table)
  - Destination field determaines what field a route matches
  - Could match specific IP or a network
  - Default route - 0.0.0.0
  - If multple routes match (/16, /32)- prefix used as priority (/32 highest)
  - Target- point as gateway or "local" - local means destination is in VPC
  - Local routes always take priority!
  - Subnet HAS to have a route table (date that LEAVES the subnet)

Internet Gateway (IGW)
*Region resilient* gateway attached to a VPC (one gateway covers ALL AZs)
- 1 VPC = 0 or 1 IGW, 1 IGW = 0 or 1 VPC
- Runs from border of VPC, within AWS Public Zone
- Gateway traffic between the VPC and the Internet or AWS Public Zone
- Managed by AWS (simply works!)
- Steps:
  - Create IGW
  - Attach IGW to VPC
  - Create custom route table
  - Assiciate RT
  - Default Routes => IGW
  - Subnet allocate IPv4
Upcoming demo!

IPv4 Addresses with a IGW
Ipv4 Instance -> IGW -> Linux Update Server (1.3.3.7)
  - 10.16.16.20, 43.250.192.20 public
    - public IP- record mtaintained by IGW, inside OS only sees private IP, public IP not actually attached to instance
    - Instance creates packet, diestination address of Linux Update Server
    - Can't reach server directly
    - Source changed to public IP address by IGW
      - Linux server sees the IGW, not the private source IP of instance
      - Linux server sends packet back to IP of IGW, which modifies destination address to the instance
    - At no point is the EC2 instance aware of its public IP, it only sees IGW!
    - IPv6 - All address are natively publically routable! No translation

Bastion Hosts = Jumpbox
- An instance in a public subnet
- Incoming management connections, then access internal VPC resources
- Management/entry point into VPC, often only way in
- Alternatives now, but will still find them

## Demo
Create IGW
Create route table, associate with web subnets
Edit route table, adding routing for 0.0.0.0/0 to IGW

In this [DEMO] Lesson we implement an Internet Gateway, Route Tables and Routes within the Animals4life VPC to support the WEB public subnets.
Once the WEB subnets are public, we create a bastion host with public IPv4 addressing and connect to it to test.
By the end of this [DEMO] you will have a fully working public capable VPC and bastion ingress point.

## Stateful vs Stateless Firewalls
TCP - connection based protocol
- 2 devices using a random port on a client (ephemeral) and a known port on the server (e.g. 80 for http and 443 for https)
- bi-directional

Client -> Server (most imagine a single outbound connection via 443/https)
- Every connection has 2 parts- REQUEST and RESPONSE
- CLient picks ephemeral poer (1024-65535 usually), initiates connection to server with well-known port (e.g. HTTPS tcp/443)
- Server responds with data, connects using source port of tcp/443 and destination ephemeral port

IP: 119.18.36.73 Request and Response -> Directionality... Inbound or Outbound depends on perspective (Client/Server) IP 1.3.3.7
- Client- Outboud, Server- Inbound
- Think about perspective when working with firewalls

Stateless Firewalls
- stateless- doesn't understand state of connections
  - sees resquest and response as 2 different parts, need 2 rules
  - server might need updates, therefore requests going OUT, response coming IN, need 2 more firewall rules
  - 2 rules for each type of connection (Inbound and Outbound)
  - Request -> well-known port
  - Response -> ephemeral port (stateless doesn't know which, so all ephemeral must be open)

Stateful Firewalls
- stateful- can identify a response for a given request as being related
- only have to allow/deny request, responcse allowed automatically
- don't need to allow full ephemeral port range

## Network Access Conrol Lists (NACLs)
Firewall available in AWS VPCs
Associated with subnets- filters data as it crosses *boundry* of subnet
- does not affect traffic within subnet

Each NACL: Inbound and Outbound rules
- stateless- only direction of traffic, not whether request or response
- rules applied in order, starting from lowest rule number
- If nothing matches a rule, implicit deny

App --- Web --- Bob
Bob uses 443 to make request, response on ephemeral port
- need an NACL associated with web subnet
- Rule 110,HTTPS-443,TCP,Port range 0.0.0.0./0, Allow
- Each network communication requires 1 request and 1 response rule
- Request to web needs request and response rule, web needs outboud rule to reach app, app needs inbound rule to accept connection
- NACL on both sides need appropriate rules

Multi-tier traffic goes through different subnets

Default NACL- automatically created with VPC
- Inbound and outbound rules have implicit deny and and Allow All rule
- Result: all traffic allowed, NACL has no effect

Custom NACL- can be created for a specific VPC
- 1 inbound rule (implicit deny), associated with no subnets initially
- Result: all traffic denied

NACL not aware of logical resources, can only be assigned to subnets
Used with Security Groups to add explicit DENY (bad IPs/Nets)
Each subnet can have one NACL (Default or Custom), single NACL can be associated with many subnets

## Security Groups (SG)
Share concepts with NACLs

Stateful- detect response traffic *automatically*
- Allowed In or Out request = allowed response
- *No Explicit Deny*... only Allow or Implicit Deny
  - Can't block specific bad actors
  - if allowed IP or range, SGs can't be used to deny subset (use NACL)
- Operate above NACLs
  - Supports IP/CIDR and logical resources, including security groups and itself
- Attached to Eleastic Network Interface (ENIs) (*not instances*, even if UI shows it this way)

SG associated with the primary ENI of an instance - allow 443 source 0.0/0/0/0
- Response flow is auto allowed if request is allowed
- Can't block specific IPs, an allow rule IN can't be overridden
  
- Capable of using Logical References 
  - web app- allow 0.0.0.0/0 (all traffic)
  - web -> app tcp/1337, reference Web SG, allow 1337 inbound, source is SG
    - rule allows all a4l-web to accress a4l-web
    - don't worry about IPs or CIDR, scales well with new instances in subnet, aplies to new automatically - reduces admin overhead
- Self References
  - Allow all traffic coming from self securty group - anything that also has that security group attached
  - handles IP changes automatically
  - cimplified management of intra-app comms
  
## Network Address Translation (NAT and NAT Gateway)
Give a private resource outgoing access only to internet
NAT - set of processes that adjust IP packets by remapping SRC or DST IPs (Static NAT)
- IP Masquerading - hide CIDR Block behind one IP (many private -> 1 public)
  - Can't initiate connections from public interenet to internal IPs

AWS - NAT Gateway

A4L App - Private, not publicly routable addresses
- need internet? Might host software update server. OR use NAT Gateway
- Public web subnet has route table attached that points at IGW
  - Private app subnet- diff route table, instead of pointing at IGW, point at NAT Gateway
    - default traffic outside subnet goes to NAT gateway (in web app subnet)
    - NAT gateway maintains translation table (change original source to be its own source), sends traffic to IGW
    - Private instance -> NAT Gateway translates address from private to NATG  -> IGW translates address from NATG to IGW

NAT Gateway must run from public subnet
Uses Elastic IPs (Static IPv4 Public)
AZ Resilient
  - For region resilience - NATGW in each AZ
  - RT for each AZ with that NATGW as target
Managed- deploy and AWS handles, scales to 45 Gbps, $ duration (~$1/day) and data volume

Implementation:
Each web subnet neets a NATGW
DB and App subnets need route tables for NATGW
NATGW is NOT regionally resilient, only in AZ (unlike IGW), must be deplyed in each AZ

EC2 Instance as NAT Instance? - Disable Source/Destination Checks (required)
- NAT Instances and NATGW are similar, NATGW preferred 
- NATGW- high end performance, scales (NOT free tier eligible)
- NAT Instance- single instance, many failure points
- When to use EC2? low volume, cheaper, test environment

## NAT Demo


