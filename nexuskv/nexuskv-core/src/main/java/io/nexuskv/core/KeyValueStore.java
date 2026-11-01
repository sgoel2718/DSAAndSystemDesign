package io.nexuskv.core;

import java.util.Optional;

/**
 * The contract every NexusKV storage engine implements.
 * Day 1: a plain in-memory version. Later days swap in the LRU cache (Day 6),
 * skip-list memtable (Day 7), WAL + SSTables (Day 14) and compaction (Day 18)
 * behind this same interface.
 */
public interface KeyValueStore extends AutoCloseable {

    /** Stores or overwrites a value. */
    void put(String key, byte[] value);

    /** Returns the value, or empty if the key is absent or deleted. */
    Optional<byte[]> get(String key);

    /** Removes the key; returns true if it existed. */
    boolean delete(String key);

    /** Number of live keys. */
    int size();

    @Override
    default void close() {}
}
