# SRE Runbook: Database QueuePool Starvation & Connection Timeouts

## Symptoms
- Applications throw `sqlalchemy.exc.TimeoutError: QueuePool limit of size N overflow M reached`.
- `/healthz` or liveness probes return HTTP 503 or fail health checks.
- Spikes in latency for read/write transaction flows.

## Root Cause Diagnostics
1. Check recent deployments to verify whether `POOL_SIZE` or `MAX_OVERFLOW` settings were reduced.
2. Inspect if long-running transactions are failing to return connections to the pool.
3. Verify if backend database connection limit was saturated.

## Standard Remediation
- Increase application database pool size: Set `POOL_SIZE >= 20` and `MAX_OVERFLOW >= 10`.
- Verify connection timeout values are at least 10–15 seconds to absorb transient spikes.
- If caused by a faulty deployment, roll back or patch the configuration file immediately.
