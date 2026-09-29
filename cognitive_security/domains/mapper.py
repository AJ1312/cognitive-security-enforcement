"""
Domain Mapping for Enterprise Industry Verticals:
- Banking & Financial Services (PSD2/SCA, AML/KYC)
- Enterprise IT / IAM (Privilege Escalation, MFA Fatigue)
- Cloud Consoles AWS/Azure/GCP (High-risk Infrastructure Changes)
- SOC Tools SIEM/SOAR (Alert Fatigue Exploitation)
Patent Reference: Section 9, Claim 12.
"""

from typing import Dict, Any, List
import numpy as np
import pandas as pd

from cognitive_security.config import CLI_WEIGHTS


class DomainMapper:
    """Maps the generic cognitive security framework to specific industry domains."""

    DOMAINS: Dict[str, Dict[str, Any]] = {
        'Banking & Financial Services': {
            'sensitive_actions': {
                'Wire transfer (> $10K)': 0.95,
                'New payee + immediate transfer': 0.90,
                'International transfer': 0.85,
                'Beneficiary detail change': 0.80,
                'Standing order modification': 0.70,
                'Credit limit increase request': 0.65,
                'Large cash withdrawal': 0.75,
                'Loan approval override': 0.85,
            },
            'signal_weights': {
                'read_to_decide_ratio': 0.25,
                'click_acceleration': 0.15,
                'scroll_velocity': 0.10,
                're_read_count': 0.10,
                'hesitation_before_confirm': 0.20,
                'task_switch_frequency': 0.10,
                'context_mismatch_score': 0.10,
            },
            'preferred_friction': ['ForcedDelay', 'ChannelEscalation', 'MandatorySummary'],
            'regulations': ['PSD2/SCA', 'AML/KYC', 'SOX', 'GLBA'],
            'attack_types': ['APP Fraud', 'BEC', 'Romance Scam', 'Vishing'],
        },
        'Enterprise IT / IAM': {
            'sensitive_actions': {
                'Global admin privilege grant': 0.95,
                'Conditional access policy change': 0.90,
                'Bulk user permission change': 0.85,
                'Certificate management': 0.85,
                'Email forwarding rule creation': 0.75,
                'Group membership modification': 0.70,
                'Application consent grant': 0.80,
                'MFA policy bypass': 0.90,
            },
            'signal_weights': {
                'read_to_decide_ratio': 0.15,
                'click_acceleration': 0.15,
                'scroll_velocity': 0.10,
                're_read_count': 0.15,
                'hesitation_before_confirm': 0.15,
                'task_switch_frequency': 0.15,
                'context_mismatch_score': 0.15,
            },
            'preferred_friction': ['StepDecomposition', 'MandatorySummary', 'ForcedDelay'],
            'regulations': ['GDPR', 'SOC2', 'ISO 27001', 'NIST CSF'],
            'attack_types': ['MFA Fatigue', 'Privilege Escalation SE', 'Credential Harvesting'],
        },
        'Cloud Consoles (AWS/Azure/GCP)': {
            'sensitive_actions': {
                'Security group: 0.0.0.0/0 rule': 0.95,
                'IAM policy with * permissions': 0.95,
                'Storage bucket public access': 0.90,
                'Production resource deletion': 0.90,
                'Cross-region data replication': 0.80,
                'Key rotation / certificate change': 0.85,
                'Network peering modification': 0.80,
                'Instance type change (production)': 0.70,
            },
            'signal_weights': {
                'read_to_decide_ratio': 0.20,
                'click_acceleration': 0.10,
                'scroll_velocity': 0.10,
                're_read_count': 0.15,
                'hesitation_before_confirm': 0.15,
                'task_switch_frequency': 0.10,
                'context_mismatch_score': 0.20,
            },
            'preferred_friction': ['StepDecomposition', 'UISimplification', 'ForcedDelay'],
            'regulations': ['SOC2', 'FedRAMP', 'ISO 27001', 'CIS Benchmarks'],
            'attack_types': ['Credential Compromise', 'Fatigue Misconfiguration', 'SE of Cloud Ops'],
        },
        'SOC Tools (SIEM/SOAR)': {
            'sensitive_actions': {
                'Alert rule suppression': 0.90,
                'Allowlist / whitelist modification': 0.85,
                'Incident closure without investigation': 0.85,
                'SOAR playbook modification': 0.90,
                'Alert priority downgrade': 0.75,
                'IOC whitelisting': 0.80,
                'Automated response config change': 0.85,
                'Bulk alert dismissal': 0.80,
            },
            'signal_weights': {
                'read_to_decide_ratio': 0.10,
                'click_acceleration': 0.10,
                'scroll_velocity': 0.05,
                're_read_count': 0.10,
                'hesitation_before_confirm': 0.15,
                'task_switch_frequency': 0.25,
                'context_mismatch_score': 0.25,
            },
            'preferred_friction': ['ForcedDelay', 'MandatorySummary', 'StepDecomposition'],
            'regulations': ['SOC2', 'NIST 800-61', 'ISO 27035', 'MITRE ATT&CK'],
            'attack_types': ['Alert Fatigue Exploitation', 'Playbook Manipulation', 'Shift-End Fatigue'],
        },
    }

    def get_comparison_table(self) -> pd.DataFrame:
        """Generate structured comparison table across domains."""
        rows = []
        for domain, config in self.DOMAINS.items():
            rows.append({
                'Domain': domain,
                'Critical Actions': len(config['sensitive_actions']),
                'Avg Sensitivity': float(np.mean(list(config['sensitive_actions'].values()))),
                'Top Friction': config['preferred_friction'][0],
                'Key Regulation': config['regulations'][0],
                'Primary Attack': config['attack_types'][0],
            })
        return pd.DataFrame(rows)
