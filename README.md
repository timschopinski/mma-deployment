# deployment-commands

Connect with ssh
```
ssh rsww@172.20.83.101
ssh hdoop@student-swarm01.maas
```

Go to project
```
cd /opt/storage/actina15-20/block-storage/students/projects/students-swarm-services/BE_188749
```

Deploy
```
docker stack deploy -c docker-compose.yml BE_188749 --with-registry-auth
```

List services
```
docker service ls
```

Print logs
```
docker service logs <container_id>
```

Build prestashop channel
```
ssh -L localhost:8080:student-swarm01.maas:18874 rsww@172.20.83.101
```

Build mysql admin channel
```
ssh -L localhost:9099:student-swarm01.maas:18874 rsww@172.20.83.101
```

Remove stack
```
docker stack rm BE_188749
```

DB Connection

psdata\app\config\parameters.php
'database_host' => 'db',
    'database_port' => '3306',
    'database_name' => 'BE_188749',
    'database_user' => 'root',
    'database_password' => 'student',
