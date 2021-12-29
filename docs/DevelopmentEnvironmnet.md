# Development

## Docker

Build docker image:
```
docker-compose build
```

Execute services in background:
```
docker-compose up -d
```

Access container:
```
docker-compose exec engine /bin/bash
```

Access development environment folder, which is a mounted volume from your own system:
```
cd /development/yellowsub/
```

## Useful Commands

The following commands assume that you are in `/development/yellowsub/`.

### Load Environment Variables

```
cp .env.dist .env
set -a
source .env
```

### Install cli commands

```
pip install -e .
```

### Create Temporary Directories for Testing

```
mkdir -p tmp/{input-files,output-files}
curl https://oasis-open.github.io/cti-documentation/examples/example_json/apt1.json -o tmp/input-files/apt1.stix.json
```

### Run processor

```
processors.collectors.fileCollector.filecollector filecollector
```
