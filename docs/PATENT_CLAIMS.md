# FORMAL PATENT CLAIMS

**Title:** Cognitive-State-Aware Adaptive Information Security Enforcement  
**Applicant / Inventor:** Ajitesh Sharma  
**Jurisdiction:** Indian Patent Office (IPO)  
**Status:** Filed Patent Specification  

---

## I. Independent Claims

### **Claim 1 (System Claim)**
A computer-implemented system for adaptive information security enforcement, comprising:
**(a)** a processor;  
**(b)** a memory coupled to the processor, the memory storing instructions that, when executed by the processor, cause the system to:
> **(i)** operate a **signal collection module** that passively collects a plurality of non-biometric interaction signals from a user's interaction with a protected computing environment, wherein the interaction signals comprise at least two signals selected from the group consisting of: read-to-decide time ratios, inter-action latencies, click acceleration patterns, scroll velocity patterns, re-read frequencies, hesitation patterns before confirmation actions, task switching frequencies, typing rhythm variances, error-correction rates, and context mismatch indicators;  
> **(ii)** operate a **cognitive load processor** that computes a Cognitive Load Index (CLI) representing a weighted deviation of the collected interaction signals from an established per-user baseline for the user;  
> **(iii)** operate a **stability analyzer** that computes a Cognitive Stability Score (CSS) representing a consistency measure of decision-making behavior within a sliding time window;  
> **(iv)** operate a **vulnerability classifier** that derives a Cognitive Vulnerability State (CVS) from the computed CLI and CSS, wherein the CVS represents an inferred situational susceptibility to manipulation without classifying emotions, diagnosing mental health conditions, or storing persistent cognitive profiles;  
> **(v)** operate an **adaptive trust manager** that dynamically adjusts a session trust level using an exponential decay function based on the CVS; and  
> **(vi)** operate an **enforcement engine** that applies graduated security controls to user-initiated actions based on the session trust level in conjunction with a sensitivity classification of the requested action, wherein the security controls comprise at least one of: cognitive friction injection, action deferral, action sandboxing, or security escalation.

---

### **Claim 6 (Method Claim)**
A computer-implemented method for preventing social engineering attacks through cognitive vulnerability detection, comprising:
**(a)** passively monitoring, by a signal collection module executing on a processor, a plurality of non-biometric interaction signals from a user session within a computing environment;  
**(b)** computing, by a cognitive state inference engine, a Cognitive Load Index (CLI) as a function of weighted deviations of the monitored signals from per-user baseline values;  
**(c)** computing, by the cognitive state inference engine, a Cognitive Stability Score (CSS) as a function of decision behavior variance within a rolling time window compared to baseline variance;  
**(d)** deriving a Cognitive Vulnerability State (CVS) as a weighted combination of the CLI and a stability deficit derived from the CSS;  
**(e)** classifying the CVS into one of a plurality of vulnerability states selected from the group consisting of: normal, elevated, high, and critical;  
**(f)** upon detection of a user-initiated action classified as sensitive, computing an effective risk score as a product of the action's base sensitivity and a CVS-derived multiplier;  
**(g)** selecting, based on the effective risk score, one or more intervention mechanisms from a hierarchy of cognitive friction strategies; and  
**(h)** applying the selected intervention mechanisms to the user-initiated action before irreversible execution thereof.

---

### **Claim 11 (Non-Transitory Medium Claim)**
A non-transitory computer-readable medium storing instructions that, when executed by a processor, cause the processor to perform operations comprising:
**(a)** collecting non-biometric interaction signals from user behavior within a protected computing environment, wherein the signals are content-agnostic and comprise temporal patterns, interaction rhythm patterns, and contextual behavior patterns;  
**(b)** maintaining an ephemeral per-user baseline of the collected signals using an exponentially weighted moving average with automatic expiration;  
**(c)** computing a cognitive vulnerability metric representing deviation from the baseline in a manner consistent with cognitive overload or instability;  
**(d)** adjusting a session trust level using an asymmetric model wherein trust decays exponentially during elevated cognitive vulnerability and recovers linearly during normal cognitive states; and  
**(e)** gating sensitive user-initiated actions based on the session trust level, wherein actions exceeding a risk threshold are subjected to cognitive friction injection, deferral, sandboxing, or escalation.

---

## II. Dependent Claims

### **Claim 2 (Dependent on Claim 1 — Signal Specifics & Privacy)**
The system of Claim 1, wherein the signal collection module is further configured to:
**(a)** compute statistical features from raw interaction events within a single processing cycle;  
**(b)** discard raw interaction events after feature extraction, retaining only aggregated statistical features;  
**(c)** normalize computed features against per-user rolling baselines maintained using exponentially weighted moving averages; and  
**(d)** operate without capturing keystroke content, screen content, biometric data, or personally identifiable information.

---

### **Claim 3 (Dependent on Claim 1 — CLI Formulation)**
The system of Claim 1, wherein the Cognitive Load Index (CLI) is computed according to:
$$\text{CLI}(t) = \frac{1}{N} \sum_{i=1}^{N} w_i \cdot \left| \frac{S_i(t) - \mu_i}{\sigma_i} \right|$$
where $S_i(t)$ is the value of signal $i$ at time $t$, $\mu_i$ and $\sigma_i$ are the rolling baseline mean and standard deviation of signal $i$ for the user, $w_i$ is a configurable weight for signal $i$, and $N$ is the number of active signals; and wherein the CLI is normalized to a range of $[0, 1]$ using a sigmoid transformation.

---

### **Claim 4 (Dependent on Claim 1 — CSS Formulation)**
The system of Claim 1, wherein the Cognitive Stability Score (CSS) is computed according to:
$$\text{CSS}(t) = 1.0 - \left( 0.40 \cdot \frac{\text{Var}(D_{[t-\Delta t, t]})}{\text{Var}(D_{\text{baseline}})} + 0.35 \cdot H(A) + 0.25 \cdot R_{\text{reversal}} \right)$$
where $D_{[t-\Delta t, t]}$ represents decision latencies within a recent time window, $D_{\text{baseline}}$ represents historical decision latencies, $H(A)$ is the normalized Shannon entropy of action selections, and $R_{\text{reversal}}$ is the action reversal rate.

---

### **Claim 5 (Dependent on Claim 1 — CVS Formulation)**
The system of Claim 1, wherein the Cognitive Vulnerability State (CVS) is computed according to:
$$\text{CVS}(t) = \alpha \cdot \text{CLI}(t) + \beta \cdot (1 - \text{CSS}(t)) + \gamma \cdot \Delta \text{CLI}(t)$$
where $\alpha$, $\beta$, and $\gamma$ are configurable weights ($\alpha=0.40, \beta=0.40, \gamma=0.20$), $\Delta \text{CLI}(t) = \max(0, \text{CLI}(t) - \text{CLI}(t-1))$, and wherein the CVS is classified into discrete states using configurable thresholds: NORMAL ($<0.30$), ELEVATED ($<0.60$), HIGH ($<0.80$), and CRITICAL ($\le 1.00$).

---

### **Claim 7 (Dependent on Claim 6 — Friction Strategies)**
The method of Claim 6, wherein the cognitive friction strategies comprise at least one of:
**(a)** a temporal delay enforced before execution of the user-initiated action, wherein the delay duration is proportional to the CVS;  
**(b)** a mandatory action summary requiring the user to provide a textual description of the intended action for verification;  
**(c)** decomposition of the user-initiated action into a plurality of atomic sub-steps, each requiring individual confirmation; and  
**(d)** dynamic modification of the user interface to suppress urgency cues including countdown timers, warning colors, and exclamation marks.

---

### **Claim 8 (Dependent on Claim 6 — Action Sandboxing)**
The method of Claim 6, further comprising:
**(a)** queuing actions exceeding a deferral threshold in a time-delayed execution queue with configurable delay periods;  
**(b)** executing queued actions in a sandboxed environment with reversibility guarantees during a grace period; and  
**(c)** redirecting sensitive actions to an alternate verification channel selected from the group consisting of: a secondary device, a pre-configured approver, and an out-of-band communication channel.

---

### **Claim 9 (Dependent on Claim 6 — Asymmetric Trust)**
The method of Claim 6, wherein the session trust level follows an asymmetric model comprising:
**(a)** exponential decay according to: $T(t+1) = T(t) \cdot e^{-\alpha \cdot \text{CVS}(t)}$, where $\alpha = 0.50$; and  
**(b)** linear recovery according to: $T_{\text{recovery}}(t) = T(t) + \lambda \cdot (1 - T(t)) \cdot (1 - \text{CVS}(t))$, where $\lambda = 0.10 < \alpha$, ensuring that trust recovery is substantially slower than trust decay.

---

### **Claim 10 (Dependent on Claim 6 — Adaptive Baseline Drift Prevention)**
The method of Claim 6, wherein the per-user baseline is maintained according to:
**(a)** an exponentially weighted moving average with configurable decay that updates exclusively during normal cognitive states;  
**(b)** automatic exclusion of periods previously flagged as elevated or critical CVS from baseline updates to prevent adversarial baseline poisoning and drift; and  
**(c)** detection of rapid baseline shifts indicative of externally-induced behavioral manipulation.

---

### **Claim 12 (Dependent on Claim 11 — Domain Customization)**
The non-transitory computer-readable medium of Claim 11, wherein the protected computing environment comprises a banking or financial services application, and wherein the sensitive user-initiated actions comprise wire transfers, new payee additions, beneficiary detail changes, and payment authorizations.

---

### **Claim 13 (Dependent on Claim 11 — Volatile RAM & Non-Diagnosis)**
The non-transitory computer-readable medium of Claim 11, wherein the operations further comprise:
**(a)** performing all cognitive state computations in volatile memory only;  
**(b)** discarding all cognitive state data upon session termination;  
**(c)** refraining from generating emotion labels, mental health inferences, or persistent user risk profiles; and  
**(d)** ensuring compliance with data minimization principles of applicable privacy regulations.

---

### **Claim 14 (Dependent on Claim 11 — Ephemeral TTL Expiration)**
The non-transitory computer-readable medium of Claim 11, wherein the ephemeral per-user baseline comprises:
**(a)** a time-to-live (TTL) expiration mechanism ensuring automatic deletion after a configurable period of 60 seconds;  
**(b)** storage strictly in volatile memory with zero persistence to non-volatile disk storage; and  
**(c)** session-specific scope such that baseline data is not shared across user sessions or cross-user identifiers.

---

### **Claim 15 (Dependent on Claim 11 — Multi-Channel Escalation & SIEM)**
The non-transitory computer-readable medium of Claim 11, wherein gating sensitive user-initiated actions further comprises:
**(a)** routing actions exceeding a critical risk threshold to a pre-configured secondary approver;  
**(b)** reducing session permissions to read-only mode until the CVS returns to a normal state;  
**(c)** generating a security event record for transmission to a Security Information and Event Management (SIEM) system, wherein the event record excludes raw cognitive state data; and  
**(d)** presenting the user with an option to verify the action via an alternate communication channel.
