ml_flow:
	uv run mlflow server --host 0.0.0.0

data_preprocessing:
	cd ../.. && \
	uv run kedro run --pipeline data_preprocessing

nn_model_training:
	cd ../.. && \
	uv run kedro run --pipeline nn_model_training

nn_model_inference:
	cd ../.. && \
	uv run kedro run --pipeline nn_model_inference