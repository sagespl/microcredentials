import torch


def get_device() -> torch.device:
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def freez_model(model: torch.nn.Module) -> None:
    for param in model.parameters():
        param.requires_grad = False


def get_model_device(model: torch.nn.Module) -> torch.device:
    return next(model.parameters()).device
