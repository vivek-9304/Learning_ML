# Fashion-MNIST Classification using PyTorch ANN

A simple **Artificial Neural Network (ANN)** built from scratch using **PyTorch** to classify images from the **Fashion-MNIST** dataset.

This project focuses on understanding the fundamental workflow of a neural network — from loading and preprocessing image data to creating a custom PyTorch `Dataset`, training an ANN using backpropagation, and evaluating its performance on unseen test data.

---

## 📌 What is Fashion-MNIST?

**Fashion-MNIST** is an image classification dataset created by Zalando Research as a more challenging replacement for the original MNIST handwritten-digit dataset.

It contains grayscale images of different clothing and footwear items.

The dataset consists of:

- **60,000 training images**
- **10,000 test images**
- Each image is **28 × 28 pixels**
- Each image contains **784 pixel values**
- There are **10 different classes**

Each pixel contains an intensity value between **0 and 255**, representing how dark that pixel is.

### Dataset Structure

The CSV files contain **785 columns**:

## ⚙️ Hyperparameters Used

The final model was trained using the following hyperparameters:

| Hyperparameter | Value |
|---|---:|
| Hidden Layers | 4 |
| Neurons per Layer | 120 |
| Epochs | 30 |
| Learning Rate | 0.0006436289452104737 |
| Dropout | 0.2 |
| Batch Size | 16 |
| Optimizer | Adam |
| Weight Decay | 3.9541133083734205e-05 |

---

## 📊 Test Accuracy

The final model achieved a **test accuracy of 89.41%** on the Fashion-MNIST test dataset.

**Test Accuracy: 89.41%**