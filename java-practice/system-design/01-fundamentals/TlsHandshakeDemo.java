import javax.crypto.*;
import javax.crypto.spec.*;
import java.security.*;
import java.security.spec.*;
import java.util.*;

public class TlsHandshakeDemo {
    // The heart of TLS 1.3: ephemeral key exchange (ECDH) -> shared secret -> symmetric AES-GCM, server signs to prove identity.
    public static void main(String[] args) throws Exception {
        KeyPairGenerator ec = KeyPairGenerator.getInstance("EC"); ec.initialize(new ECGenParameterSpec("secp256r1"));
        KeyPair serverIdentity = ec.generateKeyPair();                  // long-term key (its public key is in the certificate)
        KeyPair clientEph = ec.generateKeyPair(), serverEph = ec.generateKeyPair();
        // ServerHello: server signs its ephemeral public key with its identity key
        Signature signer = Signature.getInstance("SHA256withECDSA"); signer.initSign(serverIdentity.getPrivate());
        signer.update(serverEph.getPublic().getEncoded()); byte[] sig = signer.sign();
        Signature verifier = Signature.getInstance("SHA256withECDSA"); verifier.initVerify(serverIdentity.getPublic());
        verifier.update(serverEph.getPublic().getEncoded());
        System.out.println("1. client verifies server signature (certificate key): " + verifier.verify(sig));
        byte[] clientSecret = agree(clientEph.getPrivate(), serverEph.getPublic());
        byte[] serverSecret = agree(serverEph.getPrivate(), clientEph.getPublic());
        System.out.println("2. both sides derived the same secret without sending it: " + Arrays.equals(clientSecret, serverSecret));
        SecretKey key = new SecretKeySpec(MessageDigest.getInstance("SHA-256").digest(clientSecret), 0, 16, "AES");
        byte[] iv = new byte[12]; new SecureRandom().nextBytes(iv);
        Cipher enc = Cipher.getInstance("AES/GCM/NoPadding"); enc.init(Cipher.ENCRYPT_MODE, key, new GCMParameterSpec(128, iv));
        byte[] ct = enc.doFinal("GET /account HTTP/1.1".getBytes());
        System.out.println("3. on the wire: " + ct.length + " encrypted bytes (unreadable)");
        Cipher dec = Cipher.getInstance("AES/GCM/NoPadding"); dec.init(Cipher.DECRYPT_MODE, key, new GCMParameterSpec(128, iv));
        System.out.println("4. server decrypts: " + new String(dec.doFinal(ct)));
        ct[3] ^= 1;                                                       // attacker flips a bit
        try { dec.init(Cipher.DECRYPT_MODE, key, new GCMParameterSpec(128, iv)); dec.doFinal(ct); }
        catch (AEADBadTagException e) { System.out.println("5. tampered message rejected: integrity check failed"); }
    }

    static byte[] agree(PrivateKey mine, PublicKey theirs) throws Exception {
        KeyAgreement ka = KeyAgreement.getInstance("ECDH"); ka.init(mine); ka.doPhase(theirs, true); return ka.generateSecret();
    }
}
