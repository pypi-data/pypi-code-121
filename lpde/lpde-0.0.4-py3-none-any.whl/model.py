"""
Copyright © 2022 Felix P. Kemeth

Permission is hereby granted, free of charge, to any person obtaining a copy of this software
and associated documentation files (the “Software”), to deal in the Software without
restriction, including without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from configparser import SectionProxy
from typing import Tuple

import numpy as np
import torch
from scipy.integrate import solve_ivp
from sklearn.decomposition import TruncatedSVD
from torch.utils.data import DataLoader, Dataset


class Model:
    """
    Wrapper around neural network.

    Includes functions to train and validate network.

    Args:
        dataloader_train: Dataloader with training data
        dataloader_val: Dataloader with validation or test data
        network: PyTorch module with the network topology
        config: Config with hyperparameters
    """

    def __init__(self,
                 dataloader_train: DataLoader,
                 dataloader_val: DataLoader,
                 network: torch.nn.Module,
                 config: SectionProxy):
        super().__init__()

        self.dataloader_train = dataloader_train
        self.dataloader_val = dataloader_val

        try:
            self.boundary_conditions = dataloader_train.dataset.boundary_conditions
        except NotImplementedError:
            self.boundary_conditions = None

        self.net = network
        print('Using:', self.net.device)
        self.net = self.net.to(self.net.device)

        self.criterion = torch.nn.MSELoss(reduction='sum').to(self.net.device)

        self.optimizer = torch.optim.Adam(
            self.net.parameters(),
            lr=config.getfloat('lr'),
            weight_decay=config.getfloat('weight_decay'))

        self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer,
            patience=config.getint('patience'),
            factor=config.getfloat('reduce_factor'),
            min_lr=1e-7)

    def pad(self, data: torch.Tensor, target: torch.Tensor) -> Tuple:
        """
        Pad input/target depending on boundary conditions and kernel size.

        Args:
            data: Tensor containing the X data.
            target: Tensor containing the Y data.

        Returns:
            Padded tensor containing the X data.
            Padded tensor containing the Y data.
        """
        if self.boundary_conditions == 'periodic':
            data = torch.nn.functional.pad(
                data, (self.net.get_off_set(), self.net.get_off_set()), mode='circular')
            return data, target
        if self.boundary_conditions == 'no-flux':
            data = torch.nn.functional.pad(
                data, (self.net.get_off_set(), self.net.get_off_set()), mode='reflect')
            return data, target
        return data, target[:, :, self.net.get_off_set():-self.net.get_off_set()]

    def train(self) -> float:
        """
        Train model over one epoch.

        Returns:
            Loss averaged over the training data
        """
        self.net = self.net.train()

        sum_loss, cnt = 0, 0
        for batch in self.dataloader_train:
            # zero out gradients
            self.optimizer.zero_grad()

            # move batch to device
            batch = [tensor.to(self.net.device) for tensor in batch]

            # forward
            data, target = batch[0], batch[2]
            data, target = self.pad(data, target)
            batch.pop(2)
            batch.pop(0)
            output = self.net(data, *batch)

            # compute loss
            loss = self.criterion(output, target)

            loss.backward()
            self.optimizer.step()

            # measure accuracy on batch
            sum_loss += loss
            cnt += 1

        return sum_loss / cnt

    def validate(self) -> float:
        """
        Validate model on validation set.

        Updates learning rate using scheduler.

        Updates best accuracy.

        Returns:
            Loss averaged over the validation data
        """
        self.net = self.net.eval()

        sum_loss, cnt = 0, 0
        with torch.no_grad():
            for batch in self.dataloader_val:
                # move batch to device
                batch = [tensor.to(self.net.device) for tensor in batch]

                # forward
                data, target = batch[0], batch[2]
                data, target = self.pad(data, target)
                batch.pop(2)
                batch.pop(0)
                output = self.net(data, *batch)

                # loss / accuracy
                sum_loss += self.criterion(output, target)
                cnt += 1

        # Learning Rate reduction
        self.scheduler.step(sum_loss / cnt)

        return sum_loss / cnt

    def save_network(self, model_file_name: str) -> str:
        """
        Save model to disk.

        Args:
            model_file_name: Model filename.

        Returns:
            Model filename.
        """
        torch.save(self.net.state_dict(), model_file_name)
        return model_file_name

    def load_network(self, model_file_name: str) -> None:
        """
        Load model from disk.

        Args:
            model_file_name: Model filename.
        """
        self.net.load_state_dict(torch.load(model_file_name))

    def dfdt(self,
             time: float,  # pylint: disable=unused-argument
             input_array: np.ndarray,
             delta_x: float) -> np.ndarray:
        """
        Return du/dt of the model.

        Args:
            t: Time step.
            input_array: Input snapshot.
            delta_x: Delta x of spatial grid.

        Returns:
            Time derative at each point of input snapshot.
        """
        input_array = input_array.reshape(self.net.n_vars, -1)
        input_array = torch.tensor(
            input_array, dtype=torch.get_default_dtype()).unsqueeze(0).to(self.net.device)
        # With parameters, it is not implemented yet
        if self.net.use_param:
            raise NotImplementedError
        delta_x = torch.tensor(delta_x, dtype=torch.get_default_dtype()
                               ).unsqueeze(0).to(self.net.device)
        if self.boundary_conditions == 'periodic' or self.boundary_conditions == 'no-flux':
            input_array, _ = self.pad(input_array, None)
        return self.net.forward(input_array, delta_x)[0].cpu().detach().numpy().flatten()

    def integrate_svd(self,
                      dataset: Dataset,
                      svd: TruncatedSVD,
                      idx: int,
                      horizon: int) -> np.ndarray:
        """
        Integrate idx'th snapshot of dataset for horizon time steps using Euler stepper.

        Args:
            dataset: Dataset containing snapshots
            svd: Truncated SVD for regulairzation
            idx: Index of initial snapshot
            horizon: Number of time steps to integrate forward

        Returns:
            Numpy array with integrated data
        """
        left_bounds, _, right_bounds, _, _, param = dataset.get_data(True)
        data = []
        if svd:
            data0 = svd.inverse_transform(
                svd.transform(dataset.x_data[idx].reshape(1, -1)))
        else:
            data0 = dataset.x_data[idx].reshape(1, -1)
        data.append(data0.reshape(2, -1))

        for i in range(idx, horizon+idx):
            pred_f = self.net.forward(
                torch.tensor(data[-1], dtype=torch.get_default_dtype()
                             ).unsqueeze(0).to(self.net.device),
                dataset.__getitem__(i)[1].unsqueeze(0).to(
                    self.net.device),
                torch.tensor(param[idx], dtype=torch.get_default_dtype()
                             ).unsqueeze(0).to(self.net.device)
            )[0].cpu().detach().numpy()
            prediction = data[-1][:, dataset.off_set:-
                                  dataset.off_set] + dataset.delta_t*pred_f

            prediction = np.concatenate(
                (left_bounds[i+1], prediction, right_bounds[i+1]), axis=1)
            if svd:
                prediction = svd.inverse_transform(
                    svd.transform(prediction.reshape(1, -1)))
            data.append(prediction.reshape(2, -1))
        return np.array(data)

    def integrate(self, initial_condition, pars, t_eval):
        """
        Integrate initial condition using the learned model.

        Args:
            initial_condition:  Initial snapshot.
            pars: Parameters of the system.
            t_eval: Time values at which to return solution.

        Returns:
            Time values at which the solution was evaluated
            Solution obtained from numerical integration.
        """
        print('Integrating using learned PDE.')
        sol = solve_ivp(self.dfdt, [0, t_eval[-1]], initial_condition.flatten(),
                        t_eval=t_eval, args=pars, method='RK45')
        if sol.status == -1:
            raise ValueError('Integration failed.')
        sol.y = sol.y.T
        sol.y = np.reshape(sol.y, (len(t_eval), self.net.n_vars, -1))
        return sol.t, sol.y
