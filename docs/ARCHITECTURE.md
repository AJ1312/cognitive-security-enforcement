# Technical Architecture & System Design

**Cognitive-State-Aware Adaptive Information Security Enforcement**  
*Filed Indian Patent Prototype Architecture Specification*

```
+-----------------------------------------------------------------------------------+
|                            APPLICATION LAYER (100)                                |
|          Banking Portal | Enterprise IAM | Cloud Console | SOC SIEM/SOAR          |
+-----------------------------------------------------------------------------------+
                                         │
                   Passive Telemetry     ▼
+───────────────────────────────────────────────────────────────────────────────────+
|                       COGNITIVE SECURITY MIDDLEWARE                                |
|                                                                                   |
|  [200] Signal Collection Module  ──►  [210] Interaction Event Bus                 |
|        (7 non-biometric signals)            │                                     |
|                                             ▼                                     |
|  [300] Cognitive State Inference Engine                                           |
|        ├── [310] Ephemeral Baseline Store (60s TTL, Volatile RAM)                 |
|        ├── [320] CLI Processor:  z-score deviation & sigmoid mapping             |
|        ├── [330] CSS Scorer:     variance ratio, action entropy, reversals        |
|        └── [340] CVS Classifier: α·CLI + β·(1-CSS) + γ·ΔCLI                       |
|                                             │                                     |
|                                             ▼                                     |
|  [400] Security Policy Modulation Engine                                          |
|        ├── [410] Adaptive Trust Manager: Asymmetric decay & recovery              |
|        ├── [420] Action Sensitivity Classifier (R_effective = Sensitivity*(1+CVS)) |
|        └── [430] Intervention Executor                                            |
|                  ├── [431] Cognitive Friction (Forced Delay, Summary, Steps)     |
|                  ├── [432] Trust Decay (Full -> Restricted -> Suspended)          |
|                  ├── [433] Action Sandbox (Queue, Delay Grace Period)             |
|                  └── [434] Channel Escalation (Out-of-band Approver)              |
+───────────────────────────────────────────────────────────────────────────────────+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
|                     EXISTING SECURITY INFRASTRUCTURE (600)                        |
|                     IAM / MFA / RBAC / DLP / SIEM / SOAR                          |
+-----------------------------------------------------------------------------------+
```

---

## 1. Mathematical Formulations

### 1.1 Cognitive Load Index (CLI)
The Cognitive Load Index quantifies deviation of current interaction patterns from established per-user baselines:
$$\text{CLI}_{\text{raw}}(t) = \frac{\sum_{i=1}^{N} w_i \cdot \left| \frac{S_i(t) - \mu_i}{\sigma_i} \right|}{\sum_{i=1}^{N} w_i}$$
$$\text{CLI}(t) = \sigma(2.0 \cdot (\text{CLI}_{\text{raw}}(t) - 1.5))$$
where:
- $S_i(t)$: Value of signal $i$ at time step $t$
- $\mu_i, \sigma_i$: Rolling baseline mean and standard deviation for signal $i$
- $w_i$: Configured signal weight (summing to 1.0)
- $\sigma(z) = \frac{1}{1 + e^{-z}}$: Logistic sigmoid mapping to $[0, 1]$

### 1.2 Cognitive Stability Score (CSS)
The Cognitive Stability Score measures behavioral consistency within a rolling window of recent actions ($W=10$):
$$\text{CSS}(t) = 1.0 - \left( 0.40 \cdot \min\left(\frac{\text{Var}(D_{[t-W, t]})}{\text{Var}(D_{\text{baseline}})}, 5.0\right)/5.0 + 0.35 \cdot H_N(A) + 0.25 \cdot R_{\text{reversal}} \right)$$
where:
- $D_{[t-W, t]}$: Confirmation hesitation times within rolling window
- $H_N(A) = -\frac{1}{\log_2 K} \sum_{k=1}^K p_k \log_2(p_k + 1e-10)$: Normalized Shannon entropy of action selections
- $R_{\text{reversal}} = \frac{\text{reversals}}{\max(W-2, 1)}$: Alternating pattern frequency ($A \to B \to A$)

### 1.3 Cognitive Vulnerability State (CVS)
Continuous composite score combining cognitive load, instability, and positive velocity:
$$\text{CVS}(t) = \alpha \cdot \text{CLI}(t) + \beta \cdot (1 - \text{CSS}(t)) + \gamma \cdot \max(0, \text{CLI}(t) - \text{CLI}(t-1))$$
Default coefficients: $\alpha = 0.40, \beta = 0.40, \gamma = 0.20$.

#### State Thresholds:
| State | Range | System Posture |
|---|---|---|
| **NORMAL** | $[0.00, 0.30)$ | Standard policy, full access |
| **ELEVATED** | $[0.30, 0.60)$ | Mild friction (cool-off timers: 5-15s) |
| **HIGH** | $[0.60, 0.80)$ | Strong friction, action decomposition, summaries |
| **CRITICAL** | $[0.80, 1.00]$ | Gated execution, sandboxing, out-of-band human escalation |

### 1.4 Adaptive Trust Decay & Recovery
Trust decays exponentially with vulnerability and recovers linearly at a slower rate:
$$\text{Decay: } T(t+1) = T(t) \cdot e^{-\alpha \cdot \text{CVS}(t)}, \quad \alpha = 0.50$$
$$\text{Recovery: } T_{\text{recovery}}(t) = T(t) + \lambda \cdot (1 - T(t)) \cdot (1 - \text{CVS}(t)) \cdot \Delta t, \quad \lambda = 0.10$$

---

## 2. Friction Injection Engine

Effective Risk computation:
$$R_{\text{effective}} = S_{\text{action}} \cdot (1 + \text{CVS})$$
Where $S_{\text{action}} \in [0.1, 0.95]$ represents the static sensitivity tier of the requested action.

```
       R_effective < 0.40       ──► ALLOW (standard security)
0.40 ≤ R_effective < 0.70       ──► FRICTION (Forced Delay: 5-15s)
0.70 ≤ R_effective < 1.00       ──► DECAY & PROMPT (Delay + Summary + Step Decomposition)
1.00 ≤ R_effective < 1.50       ──► DEFER (Cool-off queue, 30m delay grace period)
       R_effective ≥ 1.50       ──► BLOCK (Out-of-band secondary human approver)
```
