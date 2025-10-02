# Cisco NX-OS VxLAN/EVPN Template

Complete VxLAN/EVPN configuration templates for Cisco Nexus Spine-Leaf topology with automated deployment.

## Overview

This repository provides production-ready configuration templates for deploying VxLAN with EVPN on Cisco Nexus switches in a Spine-Leaf architecture. It includes configurations for 2 spine switches and 2 leaf switches, along with a Python automation script for streamlined deployment.

### Key Features

- **Spine-Leaf Topology**: Scalable 2-spine, 2-leaf design
- **VxLAN/EVPN**: Modern data center overlay network
- **Multi-Tenancy**: Support for multiple VRFs (Tenant-A, Tenant-B)
- **BGP Underlay & Overlay**: eBGP for underlay, EVPN for overlay
- **Anycast Gateway**: Distributed default gateway on leaf switches
- **Layer 2 & Layer 3 VNIs**: Complete L2 and L3 overlay support
- **Automated Deployment**: Python script for configuration deployment
- **Comprehensive Documentation**: Complete topology, IP scheme, and deployment guides

## Architecture

### Topology
```
            +----------+         +----------+
            | Spine-1  |         | Spine-2  |
            | AS 65000 |         | AS 65000 |
            +----+-----+         +-----+----+
                 |                     |
        +--------+--------+------------+--------+
        |                 |                     |
   +----+----+       +----+----+
   | Leaf-1  |       | Leaf-2  |
   | AS 65001|       | AS 65002|
   +---------+       +---------+
       VTEP              VTEP
```

### Components

- **Spine Switches**: Act as BGP route reflectors for EVPN overlay
- **Leaf Switches**: Act as VTEPs (VXLAN Tunnel Endpoints)
- **Underlay**: eBGP for IP fabric connectivity
- **Overlay**: EVPN for MAC/IP advertisement and tenant separation

## Repository Structure

```
.
├── README.md              # This file - project overview
├── TOPOLOGY.md            # Detailed network topology documentation
├── IP_SCHEME.md           # Complete IP addressing and BGP AS scheme
├── DEPLOYMENT.md          # Deployment instructions and procedures
├── requirements.txt       # Python dependencies
├── deploy_vxlan.py       # Automated deployment script
└── configs/
    ├── spine-1.cfg       # Spine-1 configuration
    ├── spine-2.cfg       # Spine-2 configuration
    ├── leaf-1.cfg        # Leaf-1 configuration with VxLAN/EVPN
    └── leaf-2.cfg        # Leaf-2 configuration with VxLAN/EVPN
```

## Quick Start

### Prerequisites

- Python 3.6+
- Cisco Nexus 9000 series switches (physical or NX-OSv virtual)
- NX-OS version 7.0(3)I7(1) or higher
- SSH access to switches
- Network connectivity to management interface

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/ters-golemi/Cisco-NX-OS-VxLAN-Template.git
cd Cisco-NX-OS-VxLAN-Template
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Review and customize configurations** (if needed)
   - Check `IP_SCHEME.md` for IP addressing
   - Review `configs/*.cfg` files
   - Modify management IPs if needed

### Deployment

#### Automated (Recommended)
```bash
# Deploy to all devices with verification
python deploy_vxlan.py -u admin -v

# Deploy to specific devices
python deploy_vxlan.py -u admin -d spine-1 spine-2

# Dry run (test without applying)
python deploy_vxlan.py -u admin --dry-run
```

#### Manual
```bash
# Copy config to switch and apply
scp configs/spine-1.cfg admin@192.168.1.1:
ssh admin@192.168.1.1
configure terminal
copy bootflash:spine-1.cfg running-config
copy running-config startup-config
```

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Network Design

### IP Addressing

| Function          | Network/IP         | Description           |
|-------------------|--------------------|-----------------------|
| Management        | 192.168.1.0/24     | Out-of-band mgmt      |
| Loopback (Spine)  | 10.0.0.1-2/32      | BGP Router IDs        |
| Loopback (Leaf)   | 10.0.0.11-12/32    | BGP Router IDs        |
| VTEP (Leaf)       | 10.0.0.111-112/32  | NVE source interface  |
| P2P Links         | 10.1.1.0/24        | Spine-1 to Leafs      |
| P2P Links         | 10.1.2.0/24        | Spine-2 to Leafs      |

### BGP AS Numbers

| Device   | AS Number | Role                      |
|----------|-----------|---------------------------|
| Spine-1  | 65000     | Route Reflector           |
| Spine-2  | 65000     | Route Reflector           |
| Leaf-1   | 65001     | VTEP / Route Reflector Client |
| Leaf-2   | 65002     | VTEP / Route Reflector Client |

### VxLAN VNI Mapping

#### Layer 2 VNIs
| VLAN | VNI   | Description      | Tenant   |
|------|-------|------------------|----------|
| 10   | 10010 | Web Servers      | Tenant-A |
| 20   | 10020 | App Servers      | Tenant-A |
| 30   | 10030 | Web Servers      | Tenant-B |

#### Layer 3 VNIs
| VRF      | VNI   | Description           |
|----------|-------|-----------------------|
| Tenant-A | 50001 | L3VNI for Tenant-A    |
| Tenant-B | 50002 | L3VNI for Tenant-B    |

For complete details, see [IP_SCHEME.md](IP_SCHEME.md) and [TOPOLOGY.md](TOPOLOGY.md).

## Configuration Features

### Spine Switches
- BGP route reflector for EVPN
- eBGP underlay peering with leaf switches
- Optimized for scalability and redundancy

### Leaf Switches
- VxLAN VTEP functionality
- EVPN for MAC/IP learning
- Multiple VRFs for tenant isolation
- Anycast gateway for distributed default gateway
- L2 and L3 VNI support

## Verification Commands

After deployment, verify the configuration:

```bash
# BGP Status
show bgp summary
show bgp l2vpn evpn summary

# VxLAN Status (on leaf switches)
show nve peers
show nve interface nve1
show vxlan

# EVPN Routes
show bgp l2vpn evpn
show l2route evpn mac all

# Interface Status
show ip interface brief
show interface status
```

## Customization

### Modifying IP Addresses
1. Edit `IP_SCHEME.md` to document your changes
2. Update the configuration files in `configs/`
3. Update device IPs in `deploy_vxlan.py` if management IPs change

### Adding VLANs/VNIs
1. Choose VLAN and VNI numbers (avoid conflicts)
2. Add VLAN configuration to leaf configs
3. Add VNI mapping under `interface nve1`
4. Configure EVPN for the new VNI
5. Create SVI if needed for L3 connectivity

### Scaling to More Leafs
1. Add new leaf configuration file
2. Update spine configurations with new BGP neighbors
3. Add device entry to `deploy_vxlan.py`
4. Follow consistent IP and AS numbering

## Troubleshooting

### Common Issues

**BGP not establishing**
- Check IP connectivity: `ping <neighbor-ip>`
- Verify BGP configuration: `show run bgp`
- Check BGP status: `show bgp summary`

**NVE peers not forming**
- Verify underlay connectivity: `ping <vtep-ip> source loopback1`
- Check NVE interface: `show interface nve1`
- Verify BGP EVPN: `show bgp l2vpn evpn summary`

**VNI not working**
- Check VNI configuration: `show nve vni`
- Verify EVPN routes: `show bgp l2vpn evpn`
- Check L2 route table: `show l2route evpn mac all`

For detailed troubleshooting, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Requirements

### Hardware
- Cisco Nexus 9000 Series switches
- Or Cisco Nexus 9000v (virtual) for lab/testing

### Software
- NX-OS 7.0(3)I7(1) or higher
- Python 3.6 or higher
- Netmiko library for Python

### Features Required on Switches
- `nv overlay evpn`
- `feature bgp`
- `feature fabric forwarding`
- `feature interface-vlan`
- `feature vn-segment-vlan-based`
- `feature nv overlay`

## Documentation

- **[TOPOLOGY.md](TOPOLOGY.md)** - Complete network topology with diagrams
- **[IP_SCHEME.md](IP_SCHEME.md)** - Detailed IP addressing and BGP AS scheme
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Step-by-step deployment guide

## Contributing

Contributions are welcome! Please feel free to submit issues, fork the repository, and send pull requests.

## License

This project is provided as-is for educational and production use.

## References

- [Cisco VXLAN BGP EVPN Configuration Guide](https://www.cisco.com/c/en/us/td/docs/switches/datacenter/nexus9000/sw/7-x/vxlan/configuration/guide/b_Cisco_Nexus_9000_Series_NX-OS_VXLAN_Configuration_Guide_7x.html)
- [VXLAN EVPN Multi-Site Design and Deployment](https://www.cisco.com/c/en/us/products/collateral/switches/nexus-9000-series-switches/white-paper-c11-739942.html)
- [Netmiko Documentation](https://github.com/ktbyers/netmiko)

## Support

For questions or issues:
1. Check the [DEPLOYMENT.md](DEPLOYMENT.md) troubleshooting section
2. Review Cisco documentation links above
3. Open an issue in this repository

---

**Note**: This is a template configuration. Always test in a lab environment before deploying to production. Adjust configurations according to your specific requirements and network design.
