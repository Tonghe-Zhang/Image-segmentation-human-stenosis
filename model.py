import torch
from torch import nn
from torchvision.models import resnet50


class UNet_vanilla(nn.Module):
    def __init__(self, img_ch=1, output_ch=2):
        """
        img_ch=1 because input image is a grey image, whose feature only contains one channel. 
        > Input is of shape torch.Size([4,1,512,512]), 
        where 4 is the batch size, 1 is the channel number, 512, 512 are the width and height.
        output_ch=2 because we output a black/white distribution. 
        > Output is of shape torch.Size([4, 2, 512, 512]). 
        """
        super().__init__()
        self.Maxpool = nn.MaxPool2d(kernel_size=2, stride=2)

        self.Conv1 = conv_block(ch_in=img_ch, ch_out=64)
        self.Conv2 = conv_block(ch_in=64, ch_out=128)
        self.Conv3 = conv_block(ch_in=128, ch_out=256)
        self.Conv4 = conv_block(ch_in=256, ch_out=512)
        self.Conv5 = conv_block(ch_in=512, ch_out=1024)

        self.Up5 = up_conv(ch_in=1024, ch_out=512)
        self.Up_conv5 = conv_block(ch_in=1024, ch_out=512)
        
        self.Up4 = up_conv(ch_in=512, ch_out=256)
        self.Up_conv4 = conv_block(ch_in=512, ch_out=256)

        self.Up3 = up_conv(ch_in=256, ch_out=128)
        self.Up_conv3 = conv_block(ch_in=256, ch_out=128)

        self.Up2 = up_conv(ch_in=128, ch_out=64)
        self.Up_conv2 = conv_block(ch_in=128, ch_out=64)

        self.Conv_1x1 = nn.Conv2d(64, output_ch, kernel_size=1, stride=1, padding=0)

    def forward(self, x):
        # U-net encoder
        x1 = self.Conv1(x)
        x2 = self.Maxpool(x1)
        x2 = self.Conv2(x2)
        x3 = self.Maxpool(x2)
        x3 = self.Conv3(x3)
        x4 = self.Maxpool(x3)
        x4 = self.Conv4(x4)
        x5 = self.Maxpool(x4)
        x5 = self.Conv5(x5)
        
        # U-net decoder
        d5 = self.Up5(x5)# input [4, 1024, 32, 32], output [4, 512, 64, 64]
        d5 = torch.cat((x4, d5), dim=1) # input [4, 512, 64, 64] and [4, 512, 64, 64], output [4, 1024, 64, 64]
        d5 = self.Up_conv5(d5) # input  [4, 1024, 64, 64], output [4, 512, 64, 64]
        
        d4 = self.Up4(d5)
        d4 = torch.cat((x3, d4), dim=1)
        d4 = self.Up_conv4(d4)
        
        d3 = self.Up3(d4)
        d3 = torch.cat((x2, d3), dim=1)
        d3 = self.Up_conv3(d3)

        d2 = self.Up2(d3)
        d2 = torch.cat((x1, d2), dim=1)
        d2 = self.Up_conv2(d2)
        d1 = self.Conv_1x1(d2)
        
        """
        print(f"x.shape={x.shape}")
        print(f"x1.shape={x1.shape}")
        print(f"x2.shape={x2.shape}")
        print(f"x3.shape={x3.shape}")
        print(f"x4.shape={x4.shape}")
        print(f"x5.shape={x5.shape}")
        
        print(f"d5.shape={d5.shape}")
        print(f"d4.shape={d4.shape}")
        print(f"d3.shape={d3.shape}")
        print(f"d2.shape={d2.shape}")
        print(f"d1.shape={d1.shape}")
        exit()
        """
        """
        x.shape=torch.Size([4, 1 512, 512])

        x1.shape=torch.Size([4, 64, 512, 512])
        x2.shape=torch.Size([4, 128, 256, 256])
        x3.shape=torch.Size([4, 256, 128, 128])
        x4.shape=torch.Size([4, 512, 64, 64])
        x5.shape=torch.Size([4, 1024, 32, 32])
        
        d5.shape=torch.Size([4, 512, 64, 64])
        d4.shape=torch.Size([4, 256, 128, 128])
        d3.shape=torch.Size([4, 128, 256, 256])
        d2.shape=torch.Size([4, 64, 512, 512])
        d1.shape=torch.Size([4, 2, 512, 512])
        
        output channel feature dimension is of "2",
        because it is a black/white distribution(binary distribution). "4" is the batch size, "512, 512" are the width and height.
        """
        return d1

class conv_block(nn.Module):
    def __init__(self, ch_in, ch_out):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(ch_in, ch_out, kernel_size=3, stride=1, padding=1, bias=True),
            nn.BatchNorm2d(ch_out),
            nn.ReLU(inplace=True),
            nn.Conv2d(ch_out, ch_out, kernel_size=3, stride=1, padding=1, bias=True),
            nn.BatchNorm2d(ch_out),
            nn.ReLU(inplace=True)
        )
    def forward(self, x):
        x = self.conv(x)
        return x

class up_conv(nn.Module):
    def __init__(self, ch_in, ch_out):
        super().__init__()
        self.up = nn.Sequential(
            nn.Upsample(scale_factor=2),
            nn.Conv2d(ch_in, ch_out, kernel_size=3, stride=1, padding=1, bias=True),
            nn.BatchNorm2d(ch_out),
            nn.ReLU(inplace=True)
        )
    def forward(self, x):
        x = self.up(x)
        return x
"""
> Upsample: scale the HxW dimensions by 'scale_factor' times.
Fill the additional entries with biliner or nearest interpolation etc.
> Conv2d: 
"""
class UNetDecoder(nn.Module):
    def __init__(self,output_ch:int):
        super(UNetDecoder, self).__init__()

        self.Up5 = up_conv(ch_in=1024, ch_out=512)
        self.Up_conv5 = conv_block(ch_in=1024, ch_out=512)

        self.Up4 = up_conv(ch_in=512, ch_out=256)
        self.Up_conv4 = conv_block(ch_in=512, ch_out=256)

        self.Up3 = up_conv(ch_in=256, ch_out=128)
        self.Up_conv3 = conv_block(ch_in=256, ch_out=128)

        self.Up2 = up_conv(ch_in=128, ch_out=64)
        self.Up_conv2 = conv_block(ch_in=128, ch_out=64)

        self.Conv_1x1 = nn.Conv2d(64, output_ch, kernel_size=1, stride=1, padding=0)

    def forward(self,encoded_features):
        """
        x1.shape=torch.Size([4, 64, 512, 512])
        x2.shape=torch.Size([4, 128, 256, 256])
        x3.shape=torch.Size([4, 256, 128, 128])
        x4.shape=torch.Size([4, 512, 64, 64])
        x5.shape=torch.Size([4, 1024, 32, 32])
        d5.shape=torch.Size([4, 512, 64, 64])
        d4.shape=torch.Size([4, 256, 128, 128])
        d3.shape=torch.Size([4, 128, 256, 256])
        d2.shape=torch.Size([4, 64, 512, 512])
        d1.shape=torch.Size([4, 2, 512, 512])
        """
        x1,x2,x3,x4,x5=encoded_features
        
        print(f"x1.shape={x1.shape}")
        print(f"x2.shape={x2.shape}")
        print(f"x3.shape={x3.shape}")
        print(f"x4.shape={x4.shape}")
        print(f"x5.shape={x5.shape}")
        
        # U-net decoder
        d5 = self.Up5(x5)
        d5 = torch.cat((x4, d5), dim=1)
        d5 = self.Up_conv5(d5)
        #print(f"d5.shape={d5.shape}")

        d4 = self.Up4(d5)
        d4 = torch.cat((x3, d4), dim=1)
        d4 = self.Up_conv4(d4)
        #print(f"d4.shape={d4.shape}")

        d3 = self.Up3(d4)
        d3 = torch.cat((x2, d3), dim=1)
        d3 = self.Up_conv3(d3)
        #print(f"d3.shape={d3.shape}")


        d2 = self.Up2(d3)
        d2 = torch.cat((x1, d2), dim=1)
        d2 = self.Up_conv2(d2)
        #print(f"d2.shape={d2.shape}")

        d1 = self.Conv_1x1(d2)
        #print(f"d1.shape={d1.shape}")
        return d1
        
class ResUNet(nn.Module):
    def __init__(self, num_classes=2):
        super(ResUNet, self).__init__()

        # Builing the encoder from resenet 50
        self.model = resnet50(pretrained=True)  # Load pre-trained ResNet-50        
        # freeze the pretrained encoder. only allow training of the U net decoder layers. 
        for param in self.model.parameters():
            param.requires_grad = False

        # create learnable layer 1:
        # input dimension: [N=4, 1, H=512, W=512], output dimension: [N=4, 64, H=512, W=512]
        self.conv1=nn.Conv2d(1, 64, kernel_size=3, stride=1,padding=1, bias=True)
        self.bn1=self.model.bn1
        self.maxpool1=nn.MaxPool2d(kernel_size=3, stride=1, padding=1, dilation=1, ceil_mode=False)
        self.layer1=torch.nn.Sequential(self.conv1,self.bn1, self.maxpool1)

        #create learnable layer 2:
        # input dimension: [N=4, 64, H=512, W=512], output dimension: [N=4, 128, H=256, H=256]
        self.conv2=nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1, bias=True)
        self.bn2=nn.BatchNorm2d(128, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
        self.maxpool2=nn.MaxPool2d(kernel_size=3, stride=2, padding=1, dilation=1, ceil_mode=False)
        self.layer2=nn.Sequential(self.conv2, self.bn2, self.maxpool2)
        
        # layer 3: input dimension: [N=4, 128, H=256, H=256],
        # output dimension: [4,256,128,128]
        self.conv3=nn.Conv2d(128, 256, kernel_size=3, stride=1, padding=1, bias=True)
        self.bn3=nn.BatchNorm2d(256, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
        self.maxpool3=nn.MaxPool2d(kernel_size=3, stride=2, padding=1, dilation=1, ceil_mode=False)
        self.layer3=nn.Sequential(self.conv3, self.bn3, self.maxpool3)

        #borrow other layers from resnet50
        # layer 4: input dimension: [4,256,128,128], output dimension: [4, 512, 64, 64]
        self.layer4=self.model.layer2
        # layer 5: input dimension: [4, 512, 64, 64], output dimension: [4, 1024, 32, 32]
        self.layer5=self.model.layer3
                
        # use the Unet decoder as the decoder
        self.decoder = UNetDecoder(num_classes)
        
    def forward(self, x):
        # Encoder layers forward pass
        x1=self.layer1(x)     #x1: [4, 64, 512, 512]
        x2=self.layer2(x1)    #x2: [4, 128, 256, 256]
        x3=self.layer3(x2)    #x3: [4,256,128,128]     
        x4=self.layer4(x3)	 #x4: [4, 512, 64, 64]
        x5=self.layer5(x4)    #x5: [4, 1024, 32, 32]
        encoder_embeddings=[x1,x2,x3,x4,x5]
        
       
        print(f"x.shape={x.shape}")
        print(f"x1.shape={x1.shape}")
        print(f"x2.shape={x2.shape}")
        print(f"x3.shape={x3.shape}")
        print(f"x4.shape={x4.shape}")
        print(f"x5.shape={x5.shape}")

        """
        x.shape=torch.Size([4, 1, 512, 512])
        x1.shape=torch.Size([4, 64, 128, 128])
        x2.shape=torch.Size([4, 256, 128, 128])
        x3.shape=torch.Size([4, 512, 64, 64])
        x4.shape=torch.Size([4, 1024, 32, 32])
        x5.shape=torch.Size([4, 2048, 16, 16])
        exit()
        """

        # Decoder
        d1 = self.decoder(encoder_embeddings)
        print(f"d1.shape={d1.shape}")
        return d1
