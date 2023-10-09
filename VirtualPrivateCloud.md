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

Subnet - AZ resilient