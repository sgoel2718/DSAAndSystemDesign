package io.nexuskv.core;

import org.junit.jupiter.api.Test;

import java.nio.charset.StandardCharsets;

import static org.junit.jupiter.api.Assertions.*;

class InMemoryStoreTest {

    private static byte[] b(String s) { return s.getBytes(StandardCharsets.UTF_8); }

    @Test
    void putThenGetReturnsValue() {
        KeyValueStore store = new InMemoryStore();
        store.put("city", b("Chennai"));
        assertArrayEquals(b("Chennai"), store.get("city").orElseThrow());
    }

    @Test
    void overwriteKeepsLatestValue() {
        KeyValueStore store = new InMemoryStore();
        store.put("k", b("v1"));
        store.put("k", b("v2"));
        assertArrayEquals(b("v2"), store.get("k").orElseThrow());
        assertEquals(1, store.size());
    }

    @Test
    void deleteRemovesKey() {
        KeyValueStore store = new InMemoryStore();
        store.put("k", b("v"));
        assertTrue(store.delete("k"));
        assertTrue(store.get("k").isEmpty());
        assertFalse(store.delete("k"));
    }

    @Test
    void storedValueCannotBeMutatedByCaller() {
        KeyValueStore store = new InMemoryStore();
        byte[] value = b("abc");
        store.put("k", value);
        value[0] = 'z';
        assertArrayEquals(b("abc"), store.get("k").orElseThrow());
    }

    @Test
    void nullKeyIsRejected() {
        assertThrows(NullPointerException.class, () -> new InMemoryStore().put(null, b("v")));
    }
}
