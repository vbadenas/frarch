"""
Script to train a model to classify places365 dataset.

:Description: script to train the places365 task

:Authors: victor badenas (victor.badenas@gmail.com)

:Version: 0.1.0
:Created on: 01/06/2021 11:00
"""

__title__ = "places365"
__version__ = "0.1.0"
__author__ = "victor badenas"

import logging
import os
import sys
from pathlib import Path
from pprint import pprint

import torch
from hyperpyyaml import load_hyperpyyaml

import frarch as fr

logger = logging.getLogger(__name__)

from frarch.utils.data import build_experiment_structure
from frarch.utils.stages import Stage


class PlacesTrainer(fr.train.ClassifierTrainer):
    def forward(self, batch, stage):
        inputs, _ = batch
        inputs = inputs.to(self.device)
        return self.modules.model(inputs)

    def compute_loss(self, predictions, batch, stage):
        _, labels = batch
        labels = labels.to(self.device)
        loss = self.hparams["loss"](predictions, labels)
        if "metrics" in self.hparams:
            self.hparams["metrics"].update(predictions, labels)
        return loss

    def on_stage_start(self, stage, loss=None, epoch=None):
        self.hparams["metrics"].reset()

    def on_stage_end(self, stage, loss=None, epoch=None):
        metrics = self.hparams["metrics"].get_metrics(mode="mean")
        metrics_string = "".join([f"{k}=={v:.4f}" for k, v in metrics.items()])
        logging.info(
            f"epoch {epoch}: train_loss {self.avg_train_loss:.4f} "
            f"validation_loss {loss:.4f} metrics: {metrics_string}"
        )
        if stage == Stage.VALID:
            if self.checkpointer is not None:
                metrics["train_loss"] = self.avg_train_loss
                metrics["val_loss"] = loss
                self.checkpointer.save(
                    **metrics, epoch=self.current_epoch, current_step=self.step
                )

    def save_intra_epoch_ckpt(self):
        if self.checkpointer is not None:
            self.checkpointer.save(
                epoch=self.current_epoch, current_step=self.step, intra_epoch=True
            )


if __name__ == "__main__":
    hparam_file, args = fr.parse_arguments()

    with open(hparam_file, "r") as hparam_file_handler:
        hparams = load_hyperpyyaml(
            hparam_file_handler, args, overrides_must_match=False
        )

    build_experiment_structure(
        hparam_file,
        overrides=args,
        experiment_folder=hparams["experiment_folder"],
        debug=hparams["debug"],
    )

    trainer = PlacesTrainer(
        modules=hparams["modules"],
        opt_class=hparams["opt_class"],
        hparams=hparams,
        checkpointer=hparams["checkpointer"],
    )

    trainer.fit(
        train_set=hparams["train_dataset"],
        valid_set=hparams["valid_dataset"],
        train_loader_kwargs=hparams["dataloader_options"],
        valid_loader_kwargs=hparams["dataloader_options"],
    )
