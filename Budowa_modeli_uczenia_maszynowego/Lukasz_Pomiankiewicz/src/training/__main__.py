from src.training.run_training import run_training

if __name__ == "__main__":
    model, metrics = run_training()

    print("Training completed")
    print(metrics)