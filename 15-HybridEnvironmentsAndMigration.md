# Hybrid Environments and Migration

## Border Gateway Protocol 101 (BONUS content)

Routing protocol,  used by some AWS services such as Direct Connect and Dynamic Site to Site VPNs.

- Autonomous System (AS)- routers controlled by one entity... a network in BGP
  - black boxes that abstract away detial
- ASN are unique and allocated by IANA, typically 16-bit (0-65535, 645122-65534 are private)
- BGP operates over tcp/179- it's reliable
- Not automatic- peering is manually configured
  - each system exchanges network topology info with each other
- BGP is a path-vector protocol, it exchanges the best path to a destination between peers, doesn't accout for link speed or condition, the path is called the ASPATH
- iBGP = Internal BGP- routing withing AS
- eBGP = External BGP- routing between ASs

### BGP Topology

Brisbane (ASN 200) 10.16.0.1/16 <-> Adelaide (ASN 201) 10.17.0.1/16 <-> Alice Springs (ASN 202) 10.18.0.1/16

- Brisbane routes table contains Destination, Next Hop (0.0.0.0. means local), ASPATH (i means this network)
- each peer will excahnge best path to a destination with each other, at first only itself
- Brisbane adds Destination 10.17.0.0/16, Next Hop 10.17.0.1, ASPATH 201,i
  - same for Alice Springs router destination, Brisbane now knows about both other ASs
  - Adelaide in the same way will learn about network in Alice Springs
  - Alice Springs will also learn about Brisbane and Adelaide ASs
  - networks can route traffic to other 2
- Brisbane adds another route for going other direction to Alice Springs 10.17.0.01/16
  - Destination 10.18.0.0/16, Next Hop 10.17.0.1, ASPATH 201,202,i
  - prepend own ASN onto path
- AS advertise shortest route to other systems
- end up with HA network, BGP aware of multiple routes in case one fails
  - longer paths are non-preferred, BGP prefers shortest path
- shortest connection might be slower (e.g. fiber vs satellite), but BGP would use by default
  - AS Path Prepending can be used to artificially make the satellite path look longer making the fiber path preferred
  - ASPATH 202,202,202,i
- BGP networks work together to create a dynamic topology

## IPSec VPN Fundamentals

- IPSec is a group of protocls- sets up secure tunnels across insecure networks
- ...between two peers (local and remote)
- Provides authentication... and encryption

Public Internet (insecure)- create tunnels between peers
- created as required **interesting traffic** or tunnels torn down until needed again
- Data inside tunnels is encrypted- secure connection over insecure network

- Reminder- symmetric encryption is fast... but challenging to exchange keys securely
- Asymmetric encryption is slow... but can easily exchange public keys

IPSec Phases- has two
- IKE (Internet Key Exchange) Phase 1 (slow and heavy)
  - 2 versions, 2 is newer with more fetures
  - Authenticate- pre-shared key (password)/certificate
  - using asymmetric encryption to agree on, and create a shared symmetric key
  - IKE SA (phase 1 tunnel)
- IKE Phase 2 (fast and agile)
  - uses the keys agreed in phase 1
  - agree encryption method, and keys used for bulk data transfer
  - Create IPSEC SA... phase 2 tunnel (architecturally running over phase 1)

### IKE Phase 1:

Routers authenticate- certificate of pre-shared key authentication
Diffe-Hellman (DH) Key exchange, each side creates a DH private key and derives a public key
Public keys are exchanged over the public internet
Each side takes own private key and public key from other side, independently generates the "same" shared Diffie-Hellman key
Using DH key, exchanges key material and agreements
Each side generates a symmetrical key- using DH key and exchanged material

### IKE Phase 2:

DH key on both sides, public key on both sides, established phase 1 tunnel
Symmetric key is used to encrypt and decrypt agreements and pass more key material
"Best shared" encryption and integrity methods communicated and agreed
DH key and Exchanged Key Material is used to create symmetrical IPSEC key
IPSEC key is used for bulk encryption and decryption of interesting traffic

Two types of VPNs:
- Policy-based VPN
  - rule sets match traffic -> a pair of SAs... different rules/security settings
  - same phase 1 tunne, each policy match using unique key
  - diff sec settings for diff types of traffic
  - more difficult to configure, more flexible
- Route-based VPN
  - target matching (prefix)... matches a single pair of SAs
  - Phase 1 tunnel key
  - single phase 2 tunnel running over phase 1 tunnel
  - dropped when no interesting traffic

## AWS Site-to-Site VPN

Create network link between AWS and something not AWS

- logical connection between a VPC and on-prem network encrypted using IPSec, running over the public internet
- Full HA- if you design and implement it correctly
- quick to provision... less than an hour
- Virtual Private Gateway (VGW)- gateway object, target on 1 or more route tables
- Customer Gateway (CGW)
- VPN Connection between the VGW and CGW

AWS Site-to-Site VPN
VPC (3 subnets in 3 AZs) (10.16.0.0/16) - AWS Public Zone (VGW) - Public Internet - Office (192.168.10.0/24)
Create Customer Gateway (CGW), ext IP 1.3.3.7 at Office
VGW in AWS Public Zone has physical Endpoints (HA if at least one endpoint functioning), each with public IPv4 addresses
Create VPN connection inside AWS (can be static or dynamic), create static for now, linked to Virtual Private Gateway
VPN tunnels created between each endpoint and to the Customer Gateway
  - tell AWS side what network range in use on-prem and vice versa, traffic can flow from VPC through gateway to on-prem and back again
  - single point of failure- Customer Gateway router (partial HA)
Fully HA- add another on-prem router (preferably in second building)
  - creates two more endpoints connected to same gateway on AWS side, new tunnels to second router
  - makes VGW HA, endpoints in diff AZs

Static v Dynamic (BGP) VPN
Both: VPC -> VPC Router -> VGW -> On-Prem CGW Customer router
- Static- static networking confg- static routes in route table
  - simple, just IPSec
  - restricted on LB, multi connectionfailover
- Dynamic uses BGP, routers exchange information
  - BGP configured on both customer and AWS side using ASN
  - multiple VPN connections provide HA and traffic distribution
  - Route propogation (if enabled) means routes are added to RTs automatically

VPN Considerations
- Speed limitations ~1.25 Gbps (AWS limit) (overhead on encryption/decryption)
- Latency Considerations- inconsistent, public internet (could be many hops between you and AWS endpoint)
- Cost- AWS hourly cost, GB out cost, data cap (on premises)
- Speed of setup- hours... all software defined configuration (but need BGP support for dynamic)
- Can be used as a backup for Direct Connect (DX)
- Can be used with Direct Connect (DX)

## Simple Site2Site VPN - DEMO (5 stages)

pfsense free trial: https://aws.amazon.com/marketplace/pp/prodview-gzywopzvznrr4
https://github.com/acantril/learn-cantrill-io-labs/tree/master/aws-simple-site2site-vpn
Need key pair in N Virginia region, name "infra", .pem, Create
Starting state (1-click deployment): AWS VPC with 2 subnets (2AZs), On prem router and private server (use created key pair)

### Stage 1 - Create Site2Site VPN 
Get external IP of customer router (onprem pfsense) from stack
VPC... Create VPN customer gateway... skip bgp and cert... Create
VPC... Create VPN VPG... Create, attach to VPC
VPC.... VPN site-to-site VPN connection, Visrtual private gateway (AWS side endpoint type)... select private gateway created above, customer gateway: on-prem router, routing options: static, IP prefixes- use range n on-prem env (BGP would do this automatically)... Create
Will be in Pending state for a bit... download configuration (needed to configure pfsense), choose vendor pfsense and version number

### Stage 2 - Configure onpremises Router
Ec2... Instances running... Select onprem router... monitor and troubleshoot...get system log to get username and password
  - open IPv4 address to connect to router, sign in with pw copied above, don't follow wizard
  - Interfaces... assignments.... add detected LAN interface
  - Interfaces, enable LAN interface, choose DHCP (for production, choose static), save and apply
Phase 1 and Phase 2 config for each endpoint (total of 4 configs)
Use config from downloaded file, keep file open, config for tunnel 1 and 2
IPSec Tunnel $1
  - Phase 1 configuration: Click +Add P1, Key Exchange ver IKEv1, IPv4, Interface: WAN, Remote Gateway <IP of endpoint 1 on AWS side>
  - Auth Method: Mutual PSK, Negotiation: Main, PSK from config generated by AWS
  - Encryption: AES 128, SHA1 hasg, DH Group 2(1024bit), Lifetime 28800, Dead peer detecton yes, NAT traversal auto, delay 10, maxFailures 3, Save
  - Phase 2 configuration: Show sphase 2 entries, +Add P2
  - Local network: networkk, 192.168.10.0/224 (private network in on-prem environment)
  - Remote network 10.16.0.0/16 (AWS network) 
  - Follow same process for endpoint 2
Now created Phase 1 and 2 config for both tunnels (both endpoints at AWS side)
Apply changes in pfsense, manually connect both tunnels

### Stage 3 - Routing & Security
Configure routing and security groups in both environments
AWS Side- Route tables, 3 route tables creaded by deployment
  - rt-aws attached to both subnets, can create static route or use route propagation
  - Click route propagation, enable, should pick up IP range used in on-prem env automatically
  - AWS side infra now knows how to route to on-prem
On-Prem Side
  - simulated with rt-onprem-private
  - edit routes, any traffic destined for AWS, point at pfsense firewall, enter AWS IP range (10.16.0.0/16)
  - Target: network interface within private subnet, Save
  - Both sides now know how to reach the other, but security groups in the way
On-prem firewall simulated with AWS security groups
Security Groups- AWS Side
  - Add new rule for on-prem network
  - All traffic, enter network range used by on-prem env (192.168.8.0/21), description: allow on-prem in
Security Group- On-prem Side
  - Add rule, all traffic, IP range for AWS VPC (10.16.0.0/16)
Security Group- On-prem router
  - acting as VPN endpoint, need to allow anything running on-prem to access
  - allow IP range, add rule, all traffic, find on-prem security group

### Stage 4-5 - Testing & Cleanup
Go to EC2 instances running
  - Simulated onpermRouter, onpremServer, and awsServerA
  - Open onpremServer, RDP client, connect using Fleet Manager (for graphical UI), click "get password", open FM remote desktop
  - enter user/password, connect, try pinging aws server, goes over site to site VPN to confirm it's working

Cleanup
  - Manually delete VPN config in VPC console
  - detach gateway from VPC, delete gateway, delete customer gateway, delete CF stack
  
## Direct Connect (DX) Concepts
AWS Direct Connect links your internal network to an AWS Direct Connect location over a standard Ethernet fiber-optic cable. 
One end of the cable is connected to your router, the other to an AWS Direct Connect router. 
With this connection, you can create virtual interfaces directly to public AWS services (for example, to Amazon S3) or to Amazon VPC, bypassing internet service providers in your network path. 
An AWS Direct Connect location provides access to AWS in the Region with which it is associated. You can use a single connection in a public Region or AWS GovCloud (US) to access public AWS services in all other public Regions.

- Physical connection (1, 10, or 100 Gbps)
- Business prem -> DX Location -> AWS Region
- actually ordering a port allocation at DX location
- Port hourly cost and outbound data transfer
- One allocated, you arrange connection at DX location, plan on weeks or months of time for Business prem -> DX location
- Physical cables
- Low and consistent latency + High speeds, best way to achieve highest speeds with AWS
- dedicated port means you can achieve highest possible speed
- AWS Private services (VPC) and AWS Public services - No Internet

Architecture
- Business premises -> DX Location (not owned by AWS, often regioanl large data center with space rented by AWS): AWS Directo Connect cage with endpoints + Customer or Comms Partner cage with Customer/Partner DX router
  - DX port connected to your router or Comme Partner router - Cross Connect, physical cable connecting AWS port to yours/partners
  - -> AWS Region with VPC and public zone services

## Direct Connect (DX) Resilience and HA
Understanding of failures in DX architecture
Not resilient (and how most people provision DX):
- AWS Region  -> DX Location -> Customer Premises
  - AWS region connected to all DX locations via redundant high speed connections
  - inside DX locaiton- collection of AWS DX routers, hen ordering DX connection, you get one port on a router, connect to customer or provider DX router, you arrange the connection (Cross Conncet), then connect DX location to company network
  - probably pay telecom provider to extend DX connect to on-prem network
  - What can go wrong? 7 points of failure!
    - entire DX location could fail
    - AWS DX router could fail
    - Cross connect cable could fail
    - your DX router could fail
    - extension to on-prem location could fail (long cable run)
    - failure of on-prem env
    - or on-prem router
  - DX is not resilient by default, lots of physical components that depend on each other

How to improve resilience?
- Multiple DX ports, multiple cross connects into multuiple customer routers, multiple connections to on-prem
  - architecture can tolerate a failure of one port/router/connection
  - if DX location itself fails, connectivity still lost
  - physical cable route to on-prem could be the same (single point of failure)
  - totally separate business permises increases resilience
- Extreme resilience:
  - Aws region -> 2 DX locations (with 2 DX ports each) -> 2 Business premises

## Direct Connect (DX) - Public VIF + VPN (Encryption)
Neither public or private VIFS offer any form of encryption.
Public VIFs+IPSec VPN is a way to provide access to private VPC resources, using an encrypted IPSEC tunnel for transit.

Public VIF + VPN - authenticated and encrypted tunnel
- Over DX (low latency and consistent latency)
- Uses a public VIF + VGW/TGW public endpoints
  - private VIF gives access to private IPS only, public VIF gives access to public IPs belonging to VGW/TGW
  - what is it you're trying to access? 
- VPN is transit agnostic (DX/Public internet)
- End-to-end CGW<->TGW/VGW - MACsec is single hop based
- VPNs- wide vendor support
- VPN has more cryptographic overhead compared to MACsec... limits speeds
- VPN can be used  while DX is provisioned and/or as a DX backup
  - DX primary, backup is VPN

VPNs in AWS public zone with public addressing, many hops, variable latency
Public VIF transit- direct and low latency
VPN is for when you need end to end encryption, can connect to remote regions with same equipment

Public IP? use public VIF

## Transit Gateway (TGW)

