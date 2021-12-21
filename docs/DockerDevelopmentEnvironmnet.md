# Development

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