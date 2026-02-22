# HAPI FHIR Server (Local Docker Setup)

This folder documents how to run a local HAPI FHIR server
for dataset ingestion.
## Requirements

- Docker installed
- Port 8080 available

## Stop Existing Container (If Running)

```bash
docker stop hapi-fhir
docker rm hapi-fhir
```
## Start Fresh HAPI Server

This runs the official HAPI FHIR JPA server container.
```bash
docker run -d \
  --name hapi-fhir \
  -p 8080:8080 \
  hapiproject/hapi:latest
  ```

## verify server
Open in browser, you should see a FHIR CapabilityStatement JSON.
```bash
http://localhost:8080/fhir/metadata
```

## References

**Docker Image (Used for Local Server)**  
Official HAPI FHIR JPA Server container:  
https://hub.docker.com/r/hapiproject/hapi

**Source Repository (Server Implementation Code)**  
HAPI FHIR JPA Server Starter project:  
https://github.com/hapifhir/hapi-fhir-jpaserver-starter
