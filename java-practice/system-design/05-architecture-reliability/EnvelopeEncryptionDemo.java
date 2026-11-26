import javax.crypto.*;
import javax.crypto.spec.*;
import java.security.*;
import java.util.*;

public class EnvelopeEncryptionDemo {
    // KMS holds the master key. Each file gets its own data key; only the encrypted data key is stored next to the file.
    static class Kms {
        private final SecretKey master;
        Kms() throws Exception { KeyGenerator g = KeyGenerator.getInstance("AES"); g.init(256); master = g.generateKey(); }
        byte[][] generateDataKey() throws Exception {
            KeyGenerator g = KeyGenerator.getInstance("AES"); g.init(256); SecretKey dk = g.generateKey();
            return new byte[][]{dk.getEncoded(), aes(Cipher.ENCRYPT_MODE, master, dk.getEncoded())};
        }
        byte[] decryptDataKey(byte[] enc) throws Exception { return aes(Cipher.DECRYPT_MODE, master, enc); }
    }

    static final byte[] IV = new byte[12];
    static byte[] aes(int mode, SecretKey k, byte[] data) throws Exception { Cipher c = Cipher.getInstance("AES/GCM/NoPadding"); c.init(mode, k, new GCMParameterSpec(128, IV)); return c.doFinal(data); }

    public static void main(String[] args) throws Exception {
        Kms kms = new Kms();
        byte[][] dk = kms.generateDataKey();
        byte[] ciphertext = aes(Cipher.ENCRYPT_MODE, new SecretKeySpec(dk[0], "AES"), "invoice: Rs 2,499 for Asha".getBytes());
        Arrays.fill(dk[0], (byte) 0);                                            // forget the plaintext data key
        System.out.println("stored: " + ciphertext.length + " bytes ciphertext + " + dk[1].length + " bytes encrypted data key");
        byte[] plainKey = kms.decryptDataKey(dk[1]);
        System.out.println("read  : " + new String(aes(Cipher.DECRYPT_MODE, new SecretKeySpec(plainKey, "AES"), ciphertext)));
        // Passwords: hash with salt and many iterations, never encrypt
        byte[] salt = "per-user-salt".getBytes();
        SecretKeyFactory f = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256");
        byte[] h1 = f.generateSecret(new PBEKeySpec("hunter2".toCharArray(), salt, 210_000, 256)).getEncoded();
        byte[] h2 = f.generateSecret(new PBEKeySpec("hunter2".toCharArray(), salt, 210_000, 256)).getEncoded();
        byte[] h3 = f.generateSecret(new PBEKeySpec("hunter3".toCharArray(), salt, 210_000, 256)).getEncoded();
        System.out.println("password hash check: correct=" + MessageDigest.isEqual(h1, h2) + " wrong=" + MessageDigest.isEqual(h1, h3) + " (one-way, slow on purpose)");
    }
}
