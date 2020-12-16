import numpy as np
import torch
import torchvision


def load_data(batch_size, norm_mean, norm_std):
    trans = torchvision.transforms.Compose([torchvision.transforms.ToTensor(),
                                    torchvision.transforms.Normalize((norm_mean,), (norm_std,)), ])
    train_loader = torch.utils.data.DataLoader(torchvision.datasets.MNIST('MNIST_Train_Data', train=True, download=True, transform=trans),
                                              shuffle=True, batch_size=batch_size)
    test_loader = torch.utils.data.DataLoader(torchvision.datasets.MNIST('MNIST_Test_Data', train=False, download=True, transform=trans), 
                                            shuffle=True, batch_size=batch_size)
    return train_loader, test_loader


#takes the shape of the neural network architecture and returns the appropriate nn 
#the output layer's activation function is Softmax and all the other layers' activation function is sigmoid
def init_nn(nn_shape):
    params = []

    input = nn_shape[0]
    hidden_layers = nn_shape[1:-1]
    output = nn_shape[-1]

    if len(hidden_layers) == 0:
        params.append(torch.nn.Linear(input, output))
        params.append(torch.nn.Softmax(dim=1))
    else:
        params.append(torch.nn.Linear(input, hidden_layers[0]))
        params.append(torch.nn.Sigmoid())
        for i in range(0, len(hidden_layers) - 1):
            params.append(torch.nn.Linear(hidden_layers[i], hidden_layers[i + 1]))
            params.append(torch.nn.Sigmoid())
        params.append(torch.nn.Linear(hidden_layers[-1], output))
        params.append(torch.nn.Softmax(dim=1))

    return torch.nn.Sequential(*params)

"""
hyper-parameters
"""
batch_size = 10
#normalization of data
norm_mean = 0.5
norm_std = 0.5
"""
the shape of the neural network architecture
the first value is the input_size, the last value is the output size 
the values in between are the hidden layers and their sizes 
"""
nn_shape = [784, 30, 10]
learning_rate = 3
num_epochs = 5

#loading data
train_loader, test_loader = load_data(batch_size=batch_size, norm_mean=norm_std, norm_std=norm_std)
neural_net = init_nn(nn_shape)
#print(neural_net)
optim = torch.optim.SGD(neural_net.parameters(), lr=learning_rate)

for epoch in range(num_epochs):
    for inputs, targets in train_loader:
        optim.zero_grad()
        output = neural_net(inputs.view(inputs.shape[0], -1))

        #applying the one hot transformation to the targets since they are in originally in decimal form
        targets = torch.nn.functional.one_hot(targets)
        #changing the values to float since the loss.backward() function does not like Long (integer) values
        targets = targets.to(torch.float32)
        #some of the output tensor had different shapes and would cause problem during the backward propagation so this
        #makes sure that they are the same size
        if targets.shape == output.shape:
            loss = torch.nn.MSELoss()(output, targets)
            loss.backward()
            optim.step()

#I used the code that I found from https://towardsdatascience.com/handwritten-digit-mnist-pytorch-977b5338e627
#written by Amitrajit Bose
correct_count, all_count = 0, 0
for images, labels in test_loader:
    for i in range(len(labels)):
        img = images[i].view(1, 784)
        with torch.no_grad():
            logps = neural_net(img)

        ps = torch.exp(logps)
        probab = list(ps.numpy()[0])
        pred_label = probab.index(max(probab))
        true_label = labels.numpy()[i]
        if (true_label == pred_label):
            correct_count += 1
        all_count += 1

print("Number Of Images Tested =", all_count)
print("\nnn Accuracy =", (correct_count / all_count))

