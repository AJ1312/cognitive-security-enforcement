# PATENT SPECIFICATION

**Title of the Invention:**  
COGNITIVE-STATE-AWARE ADAPTIVE INFORMATION SECURITY ENFORCEMENT

**Inventor:**  
Ajitesh Sharma  

**Jurisdiction:**  
Indian Patent Office (IPO)  

---

## 1. Field of the Invention
The present invention relates generally to the technical field of computer systems, cybersecurity, user authentication, and adaptive access control. More specifically, the present invention relates to systems, methods, and computer-readable media for dynamically inferring real-time user cognitive vulnerability from passive, non-biometric interaction telemetry and modulating security policies, cognitive friction, and session trust decay to prevent social engineering attacks, credential coercion, and unauthorized sensitive actions.

---

## 2. Background of the Invention & Prior Art Limitations

### The Fundamental Blindspot of Modern Cybersecurity
Modern enterprise cybersecurity frameworks rely on three established paradigms:
1. **User and Entity Behavior Analytics (UEBA):** Focuses on anomaly detection in access times, network IPs, file download volumes, and device fingerprints. UEBA assumes that an attacker is an unauthorized intruder or that an account is compromised. UEBA has an intrinsic blind spot: when an authorized user is actively coerced or manipulated via social engineering (e.g., Business Email Compromise, CEO fraud, phone vishing, or deepfake impersonation), the user authenticates with legitimate credentials, from a known corporate device, within business hours. UEBA registers zero anomalies.
2. **Multi-Factor Authentication (MFA) & CAPTCHA:** Static gating mechanisms that occur at authentication boundaries. They do not evaluate ongoing cognitive vulnerability and are vulnerable to MFA fatigue attacks, prompt bombing, and user-authorized push approvals under duress.
3. **Biometric Security Solutions:** Voice biometrics, facial recognition, and eye-tracking require specialized sensors, generate high privacy liabilities under GDPR, CCPA, and BIPA, and cannot reliably infer cognitive susceptibility without invasive psychological profiling.

There exists an urgent, unaddressed technical need for a content-agnostic, sensorless, privacy-preserving security enforcement mechanism that detects when an authorized human operator is cognitively compromised or manipulated, and intercedes before irreversible actions (wire transfers, IAM elevation, production data deletion) take effect.

---

## 3. Summary of the Invention

The present invention solves these limitations by establishing **Cognitive Vulnerability State (CVS)** as an active, real-time security signal derived entirely from ordinary interaction signals.

### Core Innovative Pillars:
1. **Passive Non-Biometric Signal Collection:** Monitors 7 non-invasive telemetry signals:
   - Read-to-decide latency ratio
   - Click acceleration
   - Scroll velocity
   - Re-read count
   - Hesitation before confirmation
   - Task switch frequency
   - Context mismatch score
2. **Three-Metric Cognitive State Inference:**
   - **Cognitive Load Index (CLI):** Weighted absolute z-score deviation from per-user rolling baselines, mapped through a sigmoid transform.
   - **Cognitive Stability Score (CSS):** Rolling variance ratio, action sequence Shannon entropy, and action reversal rate.
   - **Cognitive Vulnerability State (CVS):** Continuous composite score:
     $$\text{CVS}(t) = \alpha \cdot \text{CLI}(t) + \beta \cdot (1 - \text{CSS}(t)) + \gamma \cdot \Delta \text{CLI}(t)$$
     Categorized into NORMAL, ELEVATED, HIGH, and CRITICAL states.
3. **Adaptive Trust Decay Model:**
   Session trust decays exponentially during elevated CVS:
   $$T(t+1) = T(t) \cdot e^{-\alpha \cdot \text{CVS}(t)}$$
   and recovers linearly at a significantly lower rate $\lambda < \alpha$:
   $$T_{\text{recovery}}(t) = T(t) + \lambda \cdot (1 - T(t)) \cdot (1 - \text{CVS}(t))$$
   This asymmetric trust curve prevents attackers from exploiting momentary pauses in user stress.
4. **Cognitive Friction Injection & Action Sandboxing:**
   Rather than simple binary denial, the system computes effective risk $R_{\text{effective}} = S_{\text{action}} \cdot (1 + \text{CVS})$ and dispatches tailored interventions:
   - Forced cooling delays proportional to CVS
   - Mandatory textual summaries of intended action
   - Multi-step action decomposition
   - Urgency cue suppression in user interfaces
   - Action sandboxing and out-of-band escalation
5. **Privacy-Preserving Ephemeral Architecture:**
   Raw telemetry events are discarded immediately after feature extraction. Ephemeral baselines expire automatically via a 60-second TTL in volatile RAM. All session state is destroyed upon logout. No emotion, psychological diagnosis, or persistent profiling is performed.

---

## 4. Brief Description of the Drawings

- **FIGURE 1:** System Architecture Overview showing Application Layer (100), Signal Collection Module (200), Event Bus (210), Cognitive State Inference Engine (300), Ephemeral Store (310), CLI Processor (320), CSS Scorer (330), CVS Classifier (340), Security Policy Modulation Engine (400), Trust Manager (410), Action Classifier (420), Intervention Executor (430), SIEM Interface (500), and Existing Security Infrastructure (600).
- **FIGURE 2:** Cognitive State Computation Pipeline showing normalization (201), load computation (202), stability computation (203), CVS derivation (204), and state classifier (205).
- **FIGURE 3:** Intervention Decision and Execution Flowchart showing sensitive action detection (301), risk computation (302), threshold decision diamonds (303, 305, 307), and intervention dispatch blocks (304, 306, 308, 309, 310-316).
- **FIGURES 4-14:** Detailed experimental, empirical, and domain mapping figures as detailed in the prototype results.

---

## 5. Detailed Description of Preferred Embodiments

*(See `docs/ARCHITECTURE.md` and `docs/PATENT_CLAIMS.md` for complete implementation formulations and claim dependencies).*
