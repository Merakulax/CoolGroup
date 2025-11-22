/**
 * DataAggregator - Batches high-frequency sensor data for cloud upload
 * Reduces network overhead by batching 50Hz streams into 1s chunks
 */

class DataAggregator {
    private val buffer = mutableListOf<SensorPayload>()
    private var lastUploadTime = System.currentTimeMillis()
    private var uploadCallback: ((List<SensorPayload>) -> Unit)? = null

    /**
     * Append sensor reading to buffer
     * Triggers upload when batch size or time threshold reached
     */
    fun append(payload: SensorPayload) {
        buffer.add(payload)

        val elapsedTime = System.currentTimeMillis() - lastUploadTime
        if (buffer.size >= BATCH_SIZE || elapsedTime >= BATCH_INTERVAL_MS) {
            uploadBatch()
        }
    }

    /**
     * Set callback for batch upload
     */
    fun onBatchReady(callback: (List<SensorPayload>) -> Unit) {
        this.uploadCallback = callback
    }

    /**
     * Upload current batch to cloud
     */
    private fun uploadBatch() {
        if (buffer.isEmpty()) return

        val batch = buffer.toList()
        buffer.clear()
        lastUploadTime = System.currentTimeMillis()

        println("DataAggregator: Uploading batch of ${batch.size} samples")
        uploadCallback?.invoke(batch)
    }

    /**
     * Force immediate upload (e.g., when app goes to background)
     */
    fun flush() {
        uploadBatch()
    }

    /**
     * Get current buffer statistics
     */
    fun getStats(): AggregatorStats {
        return AggregatorStats(
            bufferSize = buffer.size,
            timeSinceLastUpload = System.currentTimeMillis() - lastUploadTime
        )
    }

    companion object {
        private const val BATCH_SIZE = 50  // 50 samples at 50Hz = 1 second
        private const val BATCH_INTERVAL_MS = 1000L  // 1 second max delay
    }
}

data class AggregatorStats(
    val bufferSize: Int,
    val timeSinceLastUpload: Long
)
