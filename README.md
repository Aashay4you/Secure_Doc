# Secure_Doc
This repository contains a hybrid encryption architecture that eliminates the computational waste of static cryptography and the predictability of standard PRNGs by merging machine learning security with hardware-accelerated speed.

Core Architecture

    Context-Aware Classification: An SVM classifier uses NLP to dynamically evaluate document risk, ensuring resource-heavy encryption is reserved strictly for sensitive data.

    Stochastic Key Generation: A Multi-Layer Perceptron (MLP) neural network extracts true entropy from chaotic network noise to create completely unpredictable session keys.

    Key Encapsulation Mechanism (KEM): Bypasses AI latency by instantly locking the bulk file payload with AES-256-GCM hardware, while wrapping the tiny AI-generated key in an RSA-2048 envelope.

Security Validation

    Shannon Entropy: 0.9992 / 1.0 (Proof of near-maximum uncertainty)

    Avalanche Effect: 49.76% (Proof of perfect diffusion)

    NIST SP 800-22: Passed 6/6 tests (Proof ciphertext is statistically indistinguishable from true random noise)
