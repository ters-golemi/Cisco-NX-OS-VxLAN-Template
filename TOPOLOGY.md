# Network Topology - Spine-Leaf VxLAN/EVPN

## Topology Overview

```
                    +------------+         +------------+
                    |  Spine-1   |         |  Spine-2   |
                    | 10.0.0.1/32|         | 10.0.0.2/32|
                    +-----+------+         +------+-----+
                          |                       |
                          | P2P Links             | P2P Links
           +--------------+----------+------------+--------------+
           |                         |                           |
           | e1/1                    | e1/1                      | e1/1
    +------+------+           +------+------+             +------+------+
    |   Leaf-1    |           |   Leaf-2    |             
    | 10.0.0.11/32|           | 10.0.0.12/32|             
    +-------------+           +-------------+             
```

## Device Details

### Spine Switches
- **Spine-1**: 
  - Loopback0: 10.0.0.1/32 (Router ID & BGP)
  - Management: 192.168.1.1/24
  - BGP AS: 65000
  - Role: Route Reflector

- **Spine-2**: 
  - Loopback0: 10.0.0.2/32 (Router ID & BGP)
  - Management: 192.168.1.2/24
  - BGP AS: 65000
  - Role: Route Reflector

### Leaf Switches
- **Leaf-1**: 
  - Loopback0: 10.0.0.11/32 (Router ID & BGP)
  - Loopback1: 10.0.0.111/32 (NVE/VTEP)
  - Management: 192.168.1.11/24
  - BGP AS: 65001

- **Leaf-2**: 
  - Loopback0: 10.0.0.12/32 (Router ID & BGP)
  - Loopback1: 10.0.0.112/32 (NVE/VTEP)
  - Management: 192.168.1.12/24
  - BGP AS: 65002

## Point-to-Point Links

### Spine-1 to Leaf-1
- Spine-1 e1/1: 10.1.1.0/31
- Leaf-1 e1/1: 10.1.1.1/31

### Spine-1 to Leaf-2
- Spine-1 e1/2: 10.1.1.2/31
- Leaf-2 e1/1: 10.1.1.3/31

### Spine-2 to Leaf-1
- Spine-2 e1/1: 10.1.2.0/31
- Leaf-1 e1/2: 10.1.2.1/31

### Spine-2 to Leaf-2
- Spine-2 e1/2: 10.1.2.2/31
- Leaf-2 e1/2: 10.1.2.3/31

## BGP Configuration

### AS Numbers
- Spine Layer (Route Reflectors): AS 65000
- Leaf-1: AS 65001
- Leaf-2: AS 65002

### BGP Sessions
- **eBGP**: Between Spines and Leafs (Underlay)
- **iBGP/EVPN**: Between Spines and Leafs (Overlay via Route Reflector)

## VxLAN/EVPN Details

### L2 VNI Mappings
- VLAN 10 → VNI 10010 (Tenant-A Web)
- VLAN 20 → VNI 10020 (Tenant-A App)
- VLAN 30 → VNI 10030 (Tenant-B Web)

### L3 VNI Mappings
- VRF Tenant-A → VNI 50001
- VRF Tenant-B → VNI 50002

### Route Distinguishers & Route Targets
- Leaf-1: RD 10.0.0.11:1, RT auto
- Leaf-2: RD 10.0.0.12:1, RT auto

## Features Required
- VxLAN
- EVPN
- BGP
- NV Overlay
- Interface-vlan
- OSPF (if alternative underlay needed)
- PIM (for multicast BUM traffic, optional)
