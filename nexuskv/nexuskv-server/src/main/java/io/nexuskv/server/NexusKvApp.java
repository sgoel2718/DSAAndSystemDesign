package io.nexuskv.server;

import io.nexuskv.core.InMemoryStore;
import io.nexuskv.core.KeyValueStore;

import java.nio.charset.StandardCharsets;

/** Day 1 smoke run. The real Java NIO TCP server replaces this on Day 21. */
public class NexusKvApp {
    public static void main(String[] args) {
        try (KeyValueStore store = new InMemoryStore()) {
            store.put("hello", "world".getBytes(StandardCharsets.UTF_8));
            String v = new String(store.get("hello").orElseThrow(), StandardCharsets.UTF_8);
            System.out.println("NexusKV 0.1.0 up. GET hello -> " + v + " (keys: " + store.size() + ")");
        }
    }
}
