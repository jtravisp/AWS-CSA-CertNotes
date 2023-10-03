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
- 