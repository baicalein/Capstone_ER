# HAPI FHIR Server (Local Docker Setup)

This folder documents how to run a local HAPI FHIR server for dataset ingestion.

## Requirements

- Docker installed
- Port 8080 available

## Stop Existing Container (If Running)

```bash
docker stop hapi-fhir
docker rm hapi-fhir
```

## Start Fresh HAPI Server

This pulls the latest image and runs the official HAPI FHIR JPA server container. The commands have been consolidated for easy execution.
```bash
docker pull hapiproject/hapi:latest
docker run -d --name hapi-fhir -p 8080:8080 hapiproject/hapi:latest
  ```

## Verify Server
Open in browser, you should see a FHIR CapabilityStatement JSON.
```bash
http://localhost:8080/fhir/metadata
```

## Important Note on Execution

**File Pathing:** To resolve potential environment-specific pathing errors when interacting with the server, ensure that your main execution script (run_er_snapshot.py) is located in the root directory of the project rather than a subdirectory.

## References

**Docker Image (Used for Local Server)**  
Official HAPI FHIR JPA Server container:  
https://hub.docker.com/r/hapiproject/hapi

**Source Repository (Server Implementation Code)**  
HAPI FHIR JPA Server Starter project:  
https://github.com/hapifhir/hapi-fhir-jpaserver-starter
