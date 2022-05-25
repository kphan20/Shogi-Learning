import torch
import torch.nn as nn
import torch.nn.functional as F
from variables import ACTION_SIZE

res_block_in = 256

# residual output
head_in_channels = 256


class ResBlock(nn.Module):
    def __init__(self) -> None:
        super(ResBlock, self).__init__()

        self.conv1 = nn.Conv2d(res_block_in, 256, 3, padding=1)
        self.conv_bn = nn.BatchNorm2d(256)
        self.renl1 = F.gelu
        # could potentially be the same as the first one
        self.conv2 = nn.Conv2d(256, 256, 3, padding=1)
        # potentially redundant batch norm
        self.conv_bn2 = self.conv_bn
        # make skip connection
        self.renl2 = F.gelu

    def forward(self, input):
        before_skip = self.conv_bn2(
            self.conv2(self.renl1(self.conv_bn(self.conv1(input))))
        )
        return self.renl2(before_skip + input)


class PolicyHead(nn.Module):
    def __init__(self) -> None:
        super(PolicyHead, self).__init__()
        # need to find how many in channels from residual net
        self.conv = nn.Conv2d(head_in_channels, 2, 1)
        self.conv_bn = nn.BatchNorm2d(2)
        self.renl = F.gelu
        self.size_linear = 7 * 7 * 2  # calculate this
        # outputs final probability distribution
        # softmax? what is logit probability
        self.fc = nn.Linear(self.size_linear, ACTION_SIZE)

    def forward(self, input):
        input = self.renl(self.conv_bn(self.conv(input)))
        input = input.view(-1, self.size_linear)
        return F.softmax(self.fc(input), dim=1)


class ValueHead(nn.Module):
    def __init__(self) -> None:
        super(ValueHead, self).__init__()
        self.conv = nn.Conv2d(head_in_channels, 1, 1)
        self.conv_bn = nn.BatchNorm2d(1)
        self.renl1 = F.gelu
        self.size_linear = 7 * 7
        hidden_layer = 256
        self.fc1 = nn.Linear(self.size_linear, hidden_layer)
        self.renl2 = F.gelu
        self.fc2 = nn.Linear(hidden_layer, 1)
        self.value_range = torch.tanh

    def forward(self, input):
        return self.value_range(
            self.fc2(
                self.renl2(
                    self.fc1(
                        self.renl1(self.conv_bn(self.conv(input))).view(
                            -1, self.size_linear
                        )
                    )
                )
            )
        )


BOARD_PLANES = 43


class ResCNN(nn.Module):
    def __init__(self, res_layers) -> None:
        super(ResCNN, self).__init__()
        # initial convolution - unsure of how many filters
        # and outputs
        first_conv_out = 256
        self.conv = nn.Conv2d(BOARD_PLANES, first_conv_out, 3)
        self.conv_bn = nn.BatchNorm2d(first_conv_out)
        self.renl = F.gelu
        self.res_block = ResBlock()
        res_blocks = [ResBlock() for _ in range(res_layers)]
        self.res_blocks = nn.ModuleList(res_blocks)
        self.policy_head = PolicyHead()
        self.value_head = ValueHead()
        self.layers = res_layers

    def forward(self, input):
        input = self.renl(self.conv_bn(self.conv(input)))
        for res_block in self.res_blocks:
            input = res_block(input)

        return self.policy_head(input), self.value_head(input)
