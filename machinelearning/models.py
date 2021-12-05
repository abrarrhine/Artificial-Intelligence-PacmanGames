import nn

class PerceptronModel(object):
    def __init__(self, dimensions):
        """
        Initialize a new Perceptron instance.

        A perceptron classifies data points as either belonging to a particular
        class (+1) or not (-1). `dimensions` is the dimensionality of the data.
        For example, dimensions=2 would mean that the perceptron must classify
        2D points.
        """
        self.w = nn.Parameter(1, dimensions)

    def get_weights(self):
        """
        Return a Parameter instance with the current weights of the perceptron.
        """
        return self.w

    def run(self, x):
        """
        Calculates the score assigned by the perceptron to a data point x.

        Inputs:
            x: a node with shape (1 x dimensions)
        Returns: a node containing a single number (the score)
        """
        "*** YOUR CODE HERE ***"
        return nn.DotProduct(self.w,x)

    def get_prediction(self, x):
        """
        Calculates the predicted class for a single data point `x`.

        Returns: 1 or -1
        """
        "*** YOUR CODE HERE ***"
        if nn.as_scalar(self.run(x)) >= 0:
            return 1
        else:
            return -1

    def train(self, dataset):
        """
        Train the perceptron until convergence.
        """
        "*** YOUR CODE HERE ***"
        incorrectNum = 1
        while incorrectNum  != 0:
            incorrectNum  = 0
            for x, y in dataset.iterate_once(1):
                if self.get_prediction(x) != nn.as_scalar(y):
                    incorrectNum  += 1
                    self.w.update(x,nn.as_scalar(y))

class RegressionModel(object):
    """
    A neural network model for approximating a function that maps from real
    numbers to real numbers. The network should be sufficiently large to be able
    to approximate sin(x) on the interval [-2pi, 2pi] to reasonable precision.
    """
    def __init__(self):
        # Initialize your model parameters here
        "*** YOUR CODE HERE ***"
        self.layers = 200

        self.m1 = nn.Parameter(1, self.layers)
        self.m2 = nn.Parameter(self.layers, 1)

        self.b1 = nn.Parameter(1, self.layers)
        self.b2 = nn.Parameter(1, 1)

    def run(self, x):
        """
        Runs the model for a batch of examples.

        Inputs:
            x: a node with shape (batch_size x 1)
        Returns:
            A node with shape (batch_size x 1) containing predicted y-values
        """
        "*** YOUR CODE HERE ***"
        layer = nn.ReLU(nn.AddBias(nn.Linear(x, self.m1), self.b1))
        fOfx = nn.AddBias(nn.Linear(layer, self.m2), self.b2)
        return fOfx

    def get_loss(self, x, y):
        """
        Computes the loss for a batch of examples.

        Inputs:
            x: a node with shape (batch_size x 1)
            y: a node with shape (batch_size x 1), containing the true y-values
                to be used for training
        Returns: a loss node
        """
        "*** YOUR CODE HERE ***"
        return nn.SquareLoss(self.run(x), y)

    def train(self, dataset):
        """
        Trains the model.
        """
        "*** YOUR CODE HERE ***"
        for x, y in dataset.iterate_forever(self.layers):
            if nn.as_scalar(self.get_loss(x,y)) < .02:
                break

            lossPoints = self.get_loss(x, y)
            grad_wrt_m1, grad_wrt_b1, grad_wrt_m2, grad_wrt_b2 = nn.gradients(lossPoints, [self.m1, self.b1, self.m2, self.b2])
            mult = -.06
            self.m1.update(grad_wrt_m1, mult)
            self.m2.update(grad_wrt_m2, mult)
            self.b1.update(grad_wrt_b1, mult)
            self.b2.update(grad_wrt_b2, mult)

class DigitClassificationModel(object):
    """
    A model for handwritten digit classification using the MNIST dataset.

    Each handwritten digit is a 28x28 pixel grayscale image, which is flattened
    into a 784-dimensional vector for the purposes of this model. Each entry in
    the vector is a floating point number between 0 and 1.

    The goal is to sort each digit into one of 10 classes (number 0 through 9).

    (See RegressionModel for more information about the APIs of different
    methods here. We recommend that you implement the RegressionModel before
    working on this part of the project.)
    """
    def __init__(self):
        # Initialize your model parameters here
        "*** YOUR CODE HERE ***"
        self.layers = 784
        self.m1 = nn.Parameter(self.layers, 200)
        self.b1 = nn.Parameter(1,200)

        self.m2 = nn.Parameter(200, 150)
        self.b2 = nn.Parameter(1, 150)

        self.m3 = nn.Parameter(150, 10)
        self.b3 = nn.Parameter(1, 10)

    def run(self, x):
        """
        Runs the model for a batch of examples.

        Your model should predict a node with shape (batch_size x 10),
        containing scores. Higher scores correspond to greater probability of
        the image belonging to a particular class.

        Inputs:
            x: a node with shape (batch_size x 784)
        Output:
            A node with shape (batch_size x 10) containing predicted scores
                (also called logits)
        """
        "*** YOUR CODE HERE ***"
        linear1 = nn.Linear(x, self.m1)
        bias1 = nn.AddBias(linear1, self.b1)
        relu1 = nn.ReLU(bias1)

        linear2 = nn.Linear(relu1, self.m2)
        bias2 = nn.AddBias(linear2, self.b2)
        relu2 = nn.ReLU(bias2)

        linear3 = nn.Linear(relu2, self.m3)
        bias3 = nn.AddBias(linear3, self.b3)

        return bias3

    def get_loss(self, x, y):
        """
        Computes the loss for a batch of examples.

        The correct labels `y` are represented as a node with shape
        (batch_size x 10). Each row is a one-hot vector encoding the correct
        digit class (0-9).

        Inputs:
            x: a node with shape (batch_size x 784)
            y: a node with shape (batch_size x 10)
        Returns: a loss node
        """
        "*** YOUR CODE HERE ***"
        return nn.SoftmaxLoss(self.run(x), y)

    def train(self, dataset):
        """
        Trains the model.
        """
        "*** YOUR CODE HERE ***"
        learning_rate = -.05
        while dataset.get_validation_accuracy() < .975:
            print(dataset.get_validation_accuracy())

            if (dataset.get_validation_accuracy() >= .9):
                learning_rate = -.005

            for x,y in dataset.iterate_once(10):
                lossPoints = self.get_loss(x, y)
                grad_wrt_m1, grad_wrt_b1, grad_wrt_m2, grad_wrt_b2, grad_wrt_m3, grad_wrt_b3 = nn.gradients(lossPoints, [self.m1, self.b1, self.m2, self.b2,self.m3, self.b3])

                #Update                                                                
                self.m1.update(grad_wrt_m1, learning_rate)
                self.m2.update(grad_wrt_m2, learning_rate)
                self.m3.update(grad_wrt_m3, learning_rate)

                self.b1.update(grad_wrt_b1, learning_rate)
                self.b2.update(grad_wrt_b2, learning_rate)
                self.b3.update(grad_wrt_b3, learning_rate)
