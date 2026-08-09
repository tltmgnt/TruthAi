# APL-Ω Mathematical Framework

Executable metrics live in [`apl_omega/formulas/metrics.py`](../../apl_omega/formulas/metrics.py).

## 1. System state

\[
S_t=(P_t,L_t,I_t,D_t,E_t,A_t,C_t,Q_t,K_t,F_t,R_t,M_t,T_t,H_t)
\]

Target: \(S^*\).

## 2. Topology

\[
G_t=(V_t,E_t,W_t,X_t),\quad \Delta G_t=G_{t+1}\ominus G_t
\]

## 3. Topological / capability gap

\[
\Delta_\Omega(S_t,S^*)=d_S(S_t,S^*)+\lambda_G d_G(G_t,G^*)
\]

\[
\Delta C_c=C_c^*-C_c(t),\quad \Delta C=\sum_c w_c|\Delta C_c|
\]

## 4. Interface, dependency, configuration

\[
\Gamma_I=\prod_{j=1}^{6}I_j\quad\text{or}\quad\sum w_j I_j
\]

\[
D_G=\frac{\sum w_{ij}D_{ij}}{\sum w_{ij}},\quad
CI_t=1-\frac{|\Delta K_t|}{|K_B|}
\]

## 5. Twin, verification, freshness

\[
DTI_t=1-\Delta_{DT}(t),\quad
\text{Confidence}(DT_t)\le\text{Confidence}(\text{Evidence}_t)
\]

\[
VC=\frac{|R_V|}{|R|},\quad F_e(t)=e^{-\lambda\Delta t},\quad
\Delta K\neq0\Rightarrow\text{Reverification}
\]

## 6. Trust, uncertainty, unknown index

\[
T_t=f(I_t,A_t,K_t,E_t),\quad
H(X)=-\sum P(x)\log P(x),\quad
Conf(X)=1-\frac{H(X)}{H_{\max}}
\]

\[
U_t=w_1U_{id}+w_2U_{cfg}+w_3U_{top}+w_4U_{evi}+w_5U_{env}
\]

**Unknown ≠ Normal.**

## 7. Priority, risk, criticality, resilience

\[
\Pi_i=I_i\cdot U_i\cdot P_i\cdot R_i
\]

\[
Risk_\Omega(E_i)=P_i I_i P'_i U_i R_i
\]

\[
C_i=w_1D_i+w_2I_i+w_3P_i+w_4R_i
\]

\[
R_\Omega=w_DD+w_II+w_AA+w_RR+w_VV
\]

Recovered = Operational + Configured + Verified + Trusted.

## 8. Transition validity

\[
\Phi(T_i)=f(\text{Compatibility},\text{Safety},\text{Verification},\text{Configuration},\text{Trust},\text{Resources})
\]

\[
T_i\in\mathcal{T}_{valid}\iff C_j(T_i)=1\ \forall j
\]

Invariants \(\mathcal{I}\) must hold across transitions.

## 9. Decision and objective

\[
D_t=\pi(S_t,G_t,\Delta_\Omega,U_t,\Pi_t,\mathcal{I})
\]

\[
D_t\in\{\text{Maintain},\text{Investigate},\text{Restrict},\text{Isolate},\text{Reconfigure},\text{Reverify},\text{Recover},\text{Rebaseline},\text{Escalate}\}
\]

\[
T^*=\arg\max_{T_i\in\mathcal{T}_{valid}}J(T_i)
\]

## 10. Master loop

\[
\mathcal{A}_\Omega:(S_t,G_t,E_t)\rightarrow\Delta_\Omega\rightarrow\mathcal{T}\rightarrow\mathcal{V}\rightarrow S_{t+1}
\]

\[
\forall t,\ S_t\in\mathcal{S}_{valid}
\]

**No uncontrolled material state transition.**
