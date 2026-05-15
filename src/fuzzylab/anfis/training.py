"""ANFIS training utilities.

This module provides the training loop, data loading, and utilities
for training the ANFIS network to approximate the FIS Mamdani.

Public interface
----------------
- ``load_dataset(path)``: Load CSV dataset into tensors.
- ``create_dataloaders(X, y, ...)``: Create train/val DataLoaders.
- ``train(model, train_loader, val_loader, ...)``: Training loop.
- ``TrainingConfig``: Configuration dataclass for training.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset, random_split

from fuzzylab.anfis.anfis import AnfisNet


@dataclass
class TrainingConfig:
    """Configuration for ANFIS training.

    Attributes
    ----------
    lr : float
        Learning rate for Adam optimizer (default: 1e-3).
    batch_size : int
        Batch size for DataLoader (default: 64).
    max_epochs : int
        Maximum number of training epochs (default: 500).
    patience : int
        Early stopping patience (default: 10).
    val_split : float
        Fraction of data for validation (default: 0.2).
    seed : int
        Random seed for reproducibility (default: 42).
    device : str
        Device to train on (default: "cpu").
    """

    lr: float = 1e-3
    batch_size: int = 64
    max_epochs: int = 500
    patience: int = 10
    val_split: float = 0.2
    seed: int = 42
    device: str = "cpu"
    lr_candidates: list[float] = field(default_factory=lambda: [1e-2, 1e-3, 1e-4])


@dataclass
class TrainingResult:
    """Result of a training run.

    Attributes
    ----------
    model : AnfisNet
        Trained model.
    train_losses : list[float]
        Training loss per epoch.
    val_losses : list[float]
        Validation loss per epoch.
    best_epoch : int
        Epoch with best validation loss.
    best_val_loss : float
        Best validation loss achieved.
    stopped_early : bool
        Whether training stopped early.
    """

    model: AnfisNet
    train_losses: list[float]
    val_losses: list[float]
    best_epoch: int
    best_val_loss: float
    stopped_early: bool


def load_dataset(path: str | Path) -> tuple[torch.Tensor, torch.Tensor]:
    """Load CSV dataset into input/output tensors.

    Expected CSV format: columns for inputs followed by outputs.
    Default assumes 5 input columns and 4 output columns, all normalized [0,1].

    Parameters
    ----------
    path : str or Path
        Path to CSV file.

    Returns
    -------
    X : torch.Tensor
        Input tensor of shape (n_samples, n_inputs).
    y : torch.Tensor
        Output tensor of shape (n_samples, n_outputs).
    """
    path = Path(path)

    X_list = []
    y_list = []

    with open(path, newline="") as f:
        reader = csv.reader(f)
        header = next(reader)

        n_inputs = 5
        n_outputs = len(header) - n_inputs

        for row in reader:
            values = [float(v) for v in row]
            X_list.append(values[:n_inputs])
            y_list.append(values[n_inputs:])

    X = torch.tensor(X_list, dtype=torch.float32)
    y = torch.tensor(y_list, dtype=torch.float32)

    return X, y


def create_dataloaders(
    X: torch.Tensor,
    y: torch.Tensor,
    batch_size: int = 64,
    val_split: float = 0.2,
    seed: int = 42,
    shuffle: bool = True,
) -> tuple[DataLoader, DataLoader]:
    """Create train and validation DataLoaders.

    Parameters
    ----------
    X : torch.Tensor
        Input tensor of shape (n_samples, n_inputs).
    y : torch.Tensor
        Output tensor of shape (n_samples, n_outputs).
    batch_size : int
        Batch size (default: 64).
    val_split : float
        Fraction of data for validation (default: 0.2).
    seed : int
        Random seed for split (default: 42).
    shuffle : bool
        Shuffle training data (default: True).

    Returns
    -------
    train_loader : DataLoader
        DataLoader for training set.
    val_loader : DataLoader
        DataLoader for validation set.
    """
    dataset = TensorDataset(X, y)
    n_samples = len(dataset)
    n_val = int(n_samples * val_split)
    n_train = n_samples - n_val

    generator = torch.Generator().manual_seed(seed)
    train_dataset, val_dataset = random_split(
        dataset, [n_train, n_val], generator=generator
    )

    train_loader = DataLoader(
        train_dataset, batch_size=batch_size, shuffle=shuffle, drop_last=False
    )
    val_loader = DataLoader(
        val_dataset, batch_size=batch_size, shuffle=False, drop_last=False
    )

    return train_loader, val_loader


def train(
    model: AnfisNet,
    train_loader: DataLoader,
    val_loader: DataLoader,
    config: TrainingConfig | None = None,
    callback: Callable[[int, float, float], None] | None = None,
) -> TrainingResult:
    """Train the ANFIS model.

    Parameters
    ----------
    model : AnfisNet
        ANFIS model to train.
    train_loader : DataLoader
        Training data loader.
    val_loader : DataLoader
        Validation data loader.
    config : TrainingConfig, optional
        Training configuration. Uses defaults if not provided.
    callback : callable, optional
        Called after each epoch with (epoch, train_loss, val_loss).

    Returns
    -------
    TrainingResult
        Training results including losses and best model state.
    """
    config = config or TrainingConfig()
    device = torch.device(config.device)
    model = model.to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=config.lr)
    criterion = nn.MSELoss()

    train_losses = []
    val_losses = []

    best_val_loss = float("inf")
    best_epoch = 0
    best_state = None
    patience_counter = 0

    for epoch in range(config.max_epochs):
        model.train()
        train_loss = 0.0
        n_train_batches = 0

        for X_batch, y_batch in train_loader:
            X_batch = X_batch.to(device)
            y_batch = y_batch.to(device)

            optimizer.zero_grad()
            y_pred = model(X_batch)
            loss = criterion(y_pred, y_batch)
            loss.backward()
            optimizer.step()

            train_loss += loss.item()
            n_train_batches += 1

        train_loss /= n_train_batches
        train_losses.append(train_loss)

        model.eval()
        val_loss = 0.0
        n_val_batches = 0

        with torch.no_grad():
            for X_batch, y_batch in val_loader:
                X_batch = X_batch.to(device)
                y_batch = y_batch.to(device)

                y_pred = model(X_batch)
                loss = criterion(y_pred, y_batch)

                val_loss += loss.item()
                n_val_batches += 1

        val_loss /= n_val_batches
        val_losses.append(val_loss)

        if callback:
            callback(epoch, train_loss, val_loss)

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_epoch = epoch
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            patience_counter = 0
        else:
            patience_counter += 1

        if patience_counter >= config.patience:
            break

    stopped_early = patience_counter >= config.patience

    if best_state is not None:
        model.load_state_dict(best_state)
    model = model.to(device)

    return TrainingResult(
        model=model,
        train_losses=train_losses,
        val_losses=val_losses,
        best_epoch=best_epoch,
        best_val_loss=best_val_loss,
        stopped_early=stopped_early,
    )


def save_weights(model: AnfisNet, path: str | Path) -> None:
    """Save model weights to file.

    Parameters
    ----------
    model : AnfisNet
        Model to save.
    path : str or Path
        Path to save weights.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), path)


def load_weights(model: AnfisNet, path: str | Path) -> AnfisNet:
    """Load model weights from file.

    Parameters
    ----------
    model : AnfisNet
        Model to load weights into.
    path : str or Path
        Path to weights file.

    Returns
    -------
    AnfisNet
        Model with loaded weights.
    """
    path = Path(path)
    state_dict = torch.load(path, map_location="cpu", weights_only=True)
    model.load_state_dict(state_dict)
    return model


def train_with_lr_search(
    model_factory: Callable[[], AnfisNet],
    train_loader: DataLoader,
    val_loader: DataLoader,
    config: TrainingConfig | None = None,
    verbose: bool = False,
) -> tuple[TrainingResult, float]:
    """Train with learning rate search.

    Tries each learning rate in config.lr_candidates and returns
    the result with lowest validation loss.

    Parameters
    ----------
    model_factory : callable
        Function that returns a fresh AnfisNet instance.
    train_loader : DataLoader
        Training data loader.
    val_loader : DataLoader
        Validation data loader.
    config : TrainingConfig, optional
        Training configuration.
    verbose : bool
        Print progress (default: False).

    Returns
    -------
    result : TrainingResult
        Best training result.
    best_lr : float
        Learning rate that achieved best result.
    """
    config = config or TrainingConfig()

    best_result = None
    best_lr = config.lr_candidates[0]

    for lr in config.lr_candidates:
        if verbose:
            print(f"Trying lr={lr}...")

        model = model_factory()
        lr_config = TrainingConfig(
            lr=lr,
            batch_size=config.batch_size,
            max_epochs=config.max_epochs,
            patience=config.patience,
            val_split=config.val_split,
            seed=config.seed,
            device=config.device,
        )

        result = train(model, train_loader, val_loader, lr_config)

        if verbose:
            print(f"  best_val_loss={result.best_val_loss:.6f} at epoch {result.best_epoch}")

        if best_result is None or result.best_val_loss < best_result.best_val_loss:
            best_result = result
            best_lr = lr

    return best_result, best_lr
