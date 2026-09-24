# Example attribution stage 2

Review the exact request object in `requests/example-attribution.stage2.request.json`. Return a separate raw JSON response matching `example_attribution_stage2_response_v1`, preserve the exact `request_sha256` and `blind_record_sha256`, and use the same reviewer identity as stage 1 (`/root/s23_example_attribution`). Reconcile the supplied sealed blind attributions against the supplied alignment key without changing stage 1.
