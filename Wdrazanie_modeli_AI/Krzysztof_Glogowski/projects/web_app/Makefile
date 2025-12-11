model:
	cp ../ml_pipelines/data/06_models/model.pt src/web_app/resources/model.pt

model_windows:
	copy ..\ml_pipelines\data\06_models\model.pt src\web_app\resources\model.pt

docker:
	docker compose -f src/deploy/docker/docker-compose.yaml up --build

docker_clean_up:
	docker compose -f src/deploy/docker/docker-compose.yaml down --rmi all --volumes --remove-orphans
