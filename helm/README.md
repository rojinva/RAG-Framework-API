
## Liveness/Readiness Probe.

**failureThreshold**: 3: The number of consecutive failures required to consider the container unhealthy.
**periodSeconds**: 10: The interval (in seconds) between each probe. 
In this case, the probe will run every 10 seconds. \
**timeoutSeconds**: 1: The amount of time (in seconds) the probe waits for a response before considering it a failure. 
Here, the probe will timeout after 1 second if no response is received.\
**initialDelaySeconds**: 30: The delay (in seconds) before the first probe is initiated after the container starts. 
In this case, the probe will start 30 seconds after the container begins running.
