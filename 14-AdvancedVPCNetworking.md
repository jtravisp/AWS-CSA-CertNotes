# Advanced VPC Networking

## VPC Flow Logs
Feature allowing the monitoring of traffic flow to and from interfaces within a VPC
VPC Flow logs can be added at a VPC, Subnet or Interface level.
Flow Logs DON'T monitor packet contents ... that requires a packet sniffer.
Flow Logs can be stored on S3 or CloudWatch Logs

- Capture metadata (not contents)
- attach virtual monitors in VPC
  - All ENIs in that VPC
  - Subnet- all ENIs in that subnet
  - ENIs directly
- Not realtime
- Log Destinations- S3 or CloudWatch Logs
  - S3- view directly and integrate with 3rd party product
  - CW- integrate with other AWS services
  - Also Athena for querying (ad-hoc querying engine)

VPC
  - Subnet 1
    - App server
  - Subnet 2
    - DB Primary and Replicated Standby
  - Flow logs catpured at VPC, Subnet, and Interfaces (ENIs), capture from that point downwards, e.g. captures in VPC also capture subnets
  - Subnet flow logs would capture all traffic to/from app instance in that subnet
  - Flow Log Records sent to S3 bucket or CW

VPC Flow Logs
- many fields inc.
  - scraddr
  - dstaddr
  - srcport
  - dstport
  - protocol (icmp=1, tcp=6, udp=17)
  - action
- see an accept and a reject in same flow of traffic? both a sec group and network ACL are use, restricting flow of traffic
  - sec groups- stateful
  - network ACL- stateless, traffic is 2 sep parts, so 2 log entries in flow logs
- don't log: metadata service in EC2 instance, Amazon Windows license server, Amazon DNS server

## Egress-Only Internet Gateway
Allow outbound (and response) only access to the public AWS services and Public Internet for IPv6 enabled instances or other VPC based services.
- with IPv4 addresses are private or public
  - private can't communicate with public internet or other AWS services
- NAT allows private IPs to access public networks
- ...without allowing externally initiated connection (into instance)
- with IPv6 all IPs are public
- Internet Gateway (IPv6) allows all Ips In and Out
- Egress-Only is outbound-only for IPv6

VPC
  - Subnet 1 with IPv6 instance
  - create and attach egress-only IGW to VPC, scales based on traffic
    - default route ::/0 with egress only GW as target
    - HA by default across all AZs in the region
    - inbound traffic denied
    - only outgoing connections and their response

## VPC Endpoints (Gateway)
Gateway endpoints are a type of VPC endpoint which allow access to S3 and DynamoDB without using public addressing.
Gateway endpoints add 'prefix lists' to route table, allowing the VPC router to direct traffic flow to the public services via the gateway endpoint.

- provide access to S3 and DynamoDB
  - private- allow private only resource to access S3 and DynamoDB
  - resources usually need IPv4 address or NAT gateway to access services
  - Gateway endpoint allos access without implementing that public infrstructure
- Prefix List added to route table -> Gateway Endpoint
  - traffic to those targets goes through GWEndpoint instead of InternetGW
- HA across all AZs in a region by default
- Endpoint policy is used to control what it can access
- Regional... can't access cross-region services
- Prevent leaky buckets- S3 buckets can be set to private only by allowing access only from a GW endpoint

Public Subnet Instance -> VPC Router -> IGW -> Public Resource (e.g. S3)
Private Subnet Instance -> VPC Router -> NAT GW -> VPC Router -> IGW -> Public Resource
  - resources must have public internet access, which can be a problem
GW Endpoint (associated with subnet): Private Subnet Instance -> VPC Router -> GWE -> Public Service (S3) 
  - VPC doesn't have access to internet, only service
  - GWEs are not accessible outside the VPC
  - Endpoint Policy controls what the GWE can be used for 

## VPC Endpoints (Interface)
Used to allow private IP addressing to access public AWS services.
S3 and DynamoDB are handled by gateway endpoints - other supported services are handled by interface endpoints.
Unlike gateway endpoints - interface endpoints are not highly available by default - they are normal VPC network interfaces and should be placed 1 per AZ to ensure full HA.

- provide private access to AWS public servics
- historically.... anything not S# and DDB... but S3 is now supported
- added to specific subnets- and ENI- not HA
- for HA, add one endpoint to each subnet in each AZ used in the VPC
- network access controlled via Security Groups
- Endpoint Policies- restrict what can be done
- TCP and IPv4 ONLY
- uses PrivateLink (allow 3rd part services to be injected into VPC), useful in highly regulated industries

Different from Gateway Endpoints
- Interface Endpoints primarily use DNS, network interfaces inside VPC with private IP within subnet's range
- Endpoint provides a new service endpoint DNS, e.g. vpce-123-xyz.sns.us-east-1.vpce.amazonaws.com
- Endpoint Regional DNS
- Endpoint Zonal DNS (resolves to that specific interface)
- Applications can use these, or...
- ... PrivateDNS overrides the default DNS for services

Without Interface Endpoints:
- Instance -> services address -> router -> IGW
With Interface Endpoint:
- Instance -> router -> IGW
  - no public addressing
  - Private DNS associates a private R53 hosted zone to the VPC changing the default service DNS to resolve to the interface endpoint IP

### Exam
- Gateway endpoints work using prefix lists and route tables
  - never require changes to applications, app thinks it is communicating directly with S# or DBB
- Interface endpoints use DNS and private IP address
  - use endpoint DNS names or Private DNS, allowing unmodified apps to access services
  - don't use routing, use DNS
- GW Endpoints are HA by design
- Interface Enpoints are not HA, need to put on in every AZ

## VPC Endpoints- Interface - DEMO
1-click deployment for infra
EC2 Instance Connect Public Endpoint
- normally instance needs public IP to connect to it using console UI
- Interface endpoint- connect to public endpoint with web UI, connect through to VPC interface endpoint, then to private EC2 instances (without IPv4 private IP)

A4L-PrivateEC2 Instance
- no public IPv4 address allocated
- EC2 instance connect can't connect, can use Connect using EC2 Instance Connect Endpoint
  - must create interface endpoint
- VPC -> Endpoints -> Create
  - EC2 Isntance Connect Endpoint, select VPC
  - Additional Details: preserve client IP or not (connection comes from IP address of interface endpoint)
  - Security Group required, Select subnet, Create
- Can now utilize EC2 instance endpoint to connect to private instance, try EC2 Instance Connect Endpoint again, select newly created endpoint

Go to CF, Stacks, Demo Stack, Open S3 bucket, upload lesson txt file
note: VPC has no IGW
Go to private EV2 instance, connect using EC2 Instance Connect Endpoint, has no internet connectivity and no public IP
Create a Gateway Endpoint
  - VPC console, Endpoints, Create
    - Name: PrivateVPCS3, Category: AWS Services, S3 and choose Gateway (not Interface), select VPC, choose route table (prefixes will be added for gateway endpoints)- look for app subnet route table, skip defining endpoint policy, Create
    - Go to route tables and select main route table, Destination is prefiix for S3, prefixes are added automatically by AWS
- Back to EC2 console `aws s3 ls` will now show a list of buckets
- Gateway Endpoint allows private VPC to access public space endpoint

Egress-Only Gateway
- EC2 console, run `ping -6 ipv6.google.com`, no response (unable to ping with IPv6, no gateway configured)
- VPC -> Egress-only internet gateways -> Create
  - Name A4LIPV6, select VPC, Create
- run `ping` again, still no response, need to config routing to direct traffic flow
- VPC -> Route Tables, find route table associated with VPC, select Routes, edit
  - Add route: ::/0 (all IPv6 addresses), target egress-only gateway
  - all ipv6 traffic will go to gateway
- EC2 console, will now get ping response
- gateway is stateful, will allow return traffic back in

## VPC Peering
- Service for creating private direct encrypoted network link between two VPCs *(only 2)*
- Works same/cross-region and same/cross-account
- (optional) Public Hostnames resolve to private IPs
- Same region SGs can reference peer SGs
  - diff regions- can use SGs but must reference IP addresses or ranges
- VPC peering does NOT support transitive peering
  - A -> B -> C does NOT connect A to C, they must have their own peer
- Creates logical GW object inside both VPCs
- Routing config is needed, SGs and NACLs can filter

3 VPCs:
- VPC A 10.16.0.0/16
- VPC B 10.17.0.0/16
- VPC C 10.18.0.0/16
- isolated by default
- Peer A -> B
- Peer B -> C
  - Route tables at both sides of the peering connection are needed, directing traffic flow for the remote CIDR at the peer gateway object
  - IP address ranges cannot overlap if you want to create peering connection (plan ahead, never use same address ranges in multiple VPCs)
  - no link A -> C, can't communicate through B (routing is not transitive)
- Communication is encrypted and transits over the AWS global network when using cross-region peering connections

## VPC Peering - DEMO
1-click deployment CF template, will create VPCs, I will create peering
EC2 Console, 3 instance, one in each VPC
- Connect to InstanceA using session manager, `bash`, `cd`
- Get private IP of InstanceB, try to ping, won't work
VPC Console
- Peering connections, Create (invite -> accept process)
  - Name: VPCA-VPCB, Requester VPCA, VPC Accepter is target (VPCB), Create
  - Status of peering connect with be "Pending acceptance", select and Accept request
  - next step is configuring routing, has to happen on both sides
- Vpc, Route Tables, Choose VPCA, Routes, Edit, Add route
  - 10.17.0.0/16 (VPCB CIDR range) Target VPCA-VPCB peering connection
  - Same in VPCB but in reverse, 10.16.0.0/16 target peering connection
- Security infra might still block ping
  - Edit SG for VPCs, VPCB update inbound rules, copy SG ID for VPCA, select VPCB inbound rules, add new rule:
    - allow all ICMP-IPv4 (ping) traffic, reference ID of other SG, allowing all instances in that VPC
    - ping now works from VPCA to VPCB
- Next config B to C peer, then A to C
