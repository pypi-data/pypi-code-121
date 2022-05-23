import torch
from torch import nn


class ResidualBlockGroup(nn.Module):
    def __init__(
        self,
        input_channels,
        output_channels,
        *,
        resnet_blocks_number=3,
        kernel_size=3,
        group_norm_dim=8,
        time_embedding_length=None,  # Used for embedding time step info for the diffusion model
    ) -> None:
        super().__init__()
        kernel_padding = int((kernel_size - 1) / 2)

        self.resnet_blocks = nn.ModuleList(
            [
                nn.Sequential(
                    nn.Conv2d(
                        input_channels,
                        input_channels,
                        kernel_size,
                        padding=kernel_padding,
                    ),
                    nn.GroupNorm(group_norm_dim, input_channels),
                    nn.SiLU(),
                )
                for i in range(resnet_blocks_number)
            ]
        )

        self.output_channel_conv = (
            nn.Conv2d(input_channels, output_channels, 1)
            if input_channels != output_channels
            else nn.Identity()
        )

        self.time_mlp: nn.Sequential = (
            nn.Sequential(nn.SiLU(), nn.Linear(time_embedding_length, input_channels))
            if time_embedding_length is not None
            else None
        )

    def forward(self, x, time_embedding=None) -> torch.Tensor:
        z = x

        if time_embedding is None:
            assert (
                self.time_mlp is None
            ), "No time embedding passed to the ResidualBlockGroup"
        else:
            assert (
                self.time_mlp is not None
            ), "Time embedding passed to ResidualBlockGroup but not defined in the model init"

            time_embedding = self.time_mlp(time_embedding)

            x = torch.unsqueeze(torch.unsqueeze(time_embedding, -1), -1) + x

        for residual_block in self.resnet_blocks:
            x = residual_block(x)

        x = z + x
        x = self.output_channel_conv(x)
        return x


class Unet(nn.Module):
    def __init__(
        self,
        *,
        image_size=512,
        dim_mults=(1, 2, 4, 8, 8, 16, 16),
        input_channels=6,
        channel_dim=64,
        resnet_blocks_number=3,
    ) -> None:
        super().__init__()

        self.central_image_size = image_size / (2 ** (len(dim_mults) - 1))
        print(self.central_image_size)
        assert (
            self.central_image_size >= 1
        ), "Too many layers (dim_mults). Increase image input size, or decrease the number of items in 'dim_mults'"

        self.input_channel_conv = nn.Conv2d(
            input_channels, channel_dim, kernel_size=3, padding=1
        )
