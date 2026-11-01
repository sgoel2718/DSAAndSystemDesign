package io.nexuskv.core;

import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/**
 * Day 1 baseline: HashMap-backed store. O(1) average for every operation.
 * Values are copied in and out so callers can never mutate stored bytes.
 */
public class InMemoryStore implements KeyValueStore {

    private final Map<String, byte[]> data = new HashMap<>();

    @Override
    public void put(String key, byte[] value) {
        Objects.requireNonNull(key, "key");
        Objects.requireNonNull(value, "value");
        data.put(key, Arrays.copyOf(value, value.length));
    }

    @Override
    public Optional<byte[]> get(String key) {
        byte[] v = data.get(key);
        return v == null ? Optional.empty() : Optional.of(Arrays.copyOf(v, v.length));
    }

    @Override
    public boolean delete(String key) {
        return data.remove(key) != null;
    }

    @Override
    public int size() {
        return data.size();
    }
}
