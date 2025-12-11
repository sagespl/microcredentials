from dataclasses import dataclass
from typing import Sequence

import torch
from torch import nn
from torch.nn.functional import softmax
from torch.nn.utils.rnn import pad_sequence, pack_padded_sequence


class AvgImageEncoder(nn.Module):
    def __init__(self, backbone: nn.Module):
        super().__init__()
        self.backbone = backbone
        self.output_size = backbone.num_features

    def forward(self, x: torch.Tensor, lengths: torch.Tensor) -> torch.Tensor:
        output = self.backbone(x)
        lengths: list[int] = lengths.tolist()
        sequences = torch.split(output, lengths, dim=0)
        batch_output = torch.stack([torch.mean(sec, dim=0) for sec in sequences])

        return batch_output

    def get_device(self) -> torch.device:
        return next(self.parameters()).device

    def flatten_parameters(self):
        pass


class RecursiveImageEncoder(nn.Module):
    def __init__(
        self,
        backbone: nn.Module,
        hidden_size: int = 512,
        num_layers: int = 1,
        dropout: float = 0,
    ):
        super().__init__()
        self.backbone = backbone
        self.embedding_dim = backbone.num_features
        self.rnn = nn.RNN(
            input_size=self.embedding_dim,
            hidden_size=hidden_size,
            batch_first=True,
            num_layers=num_layers,
            dropout=dropout,
        )
        self.output_size = hidden_size

    def forward(self, x: torch.Tensor, lengths: torch.Tensor):
        positional_embeddings = self._get_positional_embeddings(
            max(lengths), self.embedding_dim, x.device
        )
        output = self.backbone(x)
        lengths_list: list[int] = lengths.tolist()
        sequences = torch.split(output, lengths_list, dim=0)
        padded_sequences = pad_sequence(list(sequences), batch_first=True)
        padded_sequences += positional_embeddings
        packed_seqs = pack_padded_sequence(
            padded_sequences, lengths.cpu(), batch_first=True, enforce_sorted=True
        )
        _, last_hidden_state = self.rnn(packed_seqs)

        return last_hidden_state[-1]

    def flatten_parameters(self):
        self.rnn.flatten_parameters()

    def _get_positional_embeddings(self, seq_len: int, embedding_dim: int, device: torch.device):
        position = torch.arange(seq_len).unsqueeze(1)
        div_term = torch.exp(
            torch.arange(0, embedding_dim, 2) * (-torch.log(torch.tensor(10000.0)) / embedding_dim)
        )
        pe = torch.zeros(seq_len, embedding_dim)
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        return pe.to(device)


class MLP(nn.Module):
    def __init__(
        self,
        input_size: int,
        hidden_shape: Sequence[int],
        output_size: int,
        activation: nn.Module = nn.ReLU(),
        dropout: float = 0.0,
    ):
        super().__init__()
        self.input_size = input_size
        self.dropout = nn.Dropout(dropout) if dropout > 0 else nn.Identity()
        self.hidden = nn.Sequential(
            *self.__build_hidden_layers(input_size, hidden_shape, activation)
        )
        self.out = nn.Linear(hidden_shape[-1], output_size)

    def __build_hidden_layers(self, input_size, hidden_shape, activation):
        hidden_layers = [
            nn.Linear(input_size, hidden_shape[0]),
            activation,
            self.dropout,
        ]
        for i in range(0, len(hidden_shape) - 1):
            hidden_layers.extend(
                [
                    nn.Linear(hidden_shape[i], hidden_shape[i + 1]),
                    activation,
                    self.dropout,
                ]
            )
        return hidden_layers

    def forward(self, x):
        x = self.hidden(x)
        x = self.out(x)
        return x


class DocumentClassifier(nn.Module):
    def __init__(self, encoder: AvgImageEncoder | RecursiveImageEncoder, classification_head: MLP):
        super().__init__()
        self.encoder = encoder
        self.classification_head = classification_head

    def forward(self, x: torch.Tensor, lengths: torch.Tensor):
        output = self.encoder(x, lengths)
        output = self.classification_head(output)
        return output

    def flatten_parameters(self):
        self.encoder.flatten_parameters()

    @torch.jit.export
    def predict_proba(self, x: torch.Tensor, lengths: torch.Tensor) -> torch.Tensor:
        output = self.forward(x, lengths).squeeze(0)
        return softmax(output, dim=0).cpu()


@dataclass
class ModelState:
    model_state_dict: dict[str, torch.Tensor]
    encoder_type: str
    encoder_backbone: str
    classification_head_input_size: int
    classification_head_hidden_shape: list[int]
    classification_head_output_size: int
    classification_head_dropout: float
    encoder_rnn_hidden_size: int | None = None
    encoder_rnn_num_layers: int | None = None
    encoder_rnn_dropout: float | None = None

    @classmethod
    def from_dict(cls, input_dict: dict) -> "ModelState":
        return cls(**input_dict)
