import numpy as np
import torch


def collate_fn(
    batch: list[tuple[list[torch.Tensor], int]],
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    items_lengths = np.array([len(items_pair[0]) for items_pair in batch])
    sorted_indices = np.argsort(-items_lengths)  # sort in descending order

    items_batch = []
    items_label_batch = []

    for idx in sorted_indices:
        items, label = batch[idx]
        items_batch += [*items]
        items_label_batch.append(label)

    return (
        torch.stack(items_batch),
        torch.LongTensor(items_lengths[sorted_indices]),
        torch.LongTensor(items_label_batch),
    )


def predict_collate_fn(
    batch: list[list[torch.Tensor]],
) -> tuple[torch.Tensor, torch.Tensor]:
    items_lengths = np.array([len(items) for items in batch])
    sorted_indices = np.argsort(-items_lengths)  # sort in descending order

    items_batch = []

    for idx in sorted_indices:
        items = batch[idx]
        items_batch += [*items]

    return torch.stack(items_batch), torch.LongTensor(items_lengths[sorted_indices])
