# Azure Services Inventory (Repurposed to Hermes)

This document inventories the Azure resources currently deployed in resource group **OpenClaw** and defines their semantic role after repurposing to **Hermes**.

Reference: https://hermes-agent.nousresearch.com/docs/

## Context

- Subscription: Ant Enterprise
- Tenant: f0b2f579-2f09-4daf-839f-abf49b0d8dcc
- Current Resource Group Name: OpenClaw (legacy name)
- Strategic Purpose: Hermes runtime and supporting infrastructure

## Important Naming Note

Azure resources shown below still use legacy **openclaw-*** names in Azure. They are now semantically repurposed for Hermes workloads.

In Azure, most resource names are immutable. "Repurposed to Hermes" in this file means:
- Business/technical purpose is now Hermes
- Existing resources are retained with legacy names unless explicitly rebuilt with new Hermes names

## Services and Semantic Description

| Legacy Azure Name | Azure Resource Type | Hermes Semantic Role | Description (Hermes Context) |
|---|---|---|---|
| openclaw-vm | Microsoft.Compute/virtualMachines | Hermes Compute Runtime | Main Hermes execution host. Runs agent processes, automation tasks, and integration workloads. |
| openclaw-vm-osdisk | Microsoft.Compute/disks | Hermes Runtime State Disk | Persistent OS and runtime state for the Hermes VM, including installed services and system configuration. |
| openclaw-vm-vnet | Microsoft.Network/virtualNetworks | Hermes Network Boundary | Private network perimeter for Hermes infrastructure, isolating internal communication and defining address space. |
| openclaw-vm-nic | Microsoft.Network/networkInterfaces | Hermes VM Network Attachment | Network interface binding Hermes compute to subnet, NSG, and routing/policy controls. |
| openclaw-vm-nsg | Microsoft.Network/networkSecurityGroups | Hermes Traffic Policy Layer | Inbound/outbound security rule set that constrains Hermes host exposure to approved protocols and sources. |
| openclaw-vm-pip | Microsoft.Network/publicIPAddresses | Hermes Public Entry Point | Internet-reachable endpoint used for controlled external access to Hermes-facing services. |
| openclaw-openai | Microsoft.CognitiveServices/accounts (OpenAI) | Hermes AI Inference Service | Managed Azure OpenAI account used by Hermes for model inference, prompting workflows, and LLM-backed capabilities. |

## Operational Interpretation

- All listed resources are now part of the Hermes platform footprint.
- OpenClaw is treated as a legacy naming label only.
- New architecture, automation, and runbooks should refer to these resources as Hermes services.

## Recommended Next Step (Optional)

If you want names in Azure to match Hermes branding, create equivalent **hermes-*** resources and migrate workloads, then decommission legacy OpenClaw resources after validation.
