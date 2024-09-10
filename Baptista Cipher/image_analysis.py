import numpy as np
from skimage import io
from scipy.stats import entropy
from skimage.measure import shannon_entropy

def compute_entropy(image):
    # Compute entropy of the image
    return entropy(image.flatten())

def compute_histogram(image):
    # Compute histogram of the image
    hist, _ = np.histogram(image.flatten(), bins=256, range=(0,256))
    return hist

def compute_correlation(image):
    # Compute correlation matrix of the image
    corr_matrix = np.corrcoef(image.flatten().reshape(1,-1))
    return corr_matrix

def compute_energy(image):
    # Compute energy of the image
    return np.sum(image.astype(np.float64) ** 2)

def compute_mse(original_image, decrypted_image):
    # Compute Mean Square Error (MSE) between original and decrypted images
    mse = np.mean((original_image - decrypted_image) ** 2)
    return mse

def compute_homogeneity(image):
    # Compute homogeneity of the image
    homogeneity = np.mean(1 / (1 + (image.astype(np.float64) - np.mean(image)) ** 2))
    return homogeneity

def compute_npcr(original_image, encrypted_image):
    # Compute Normalized Pixel Change Rate (NPCR)
    npc_rate = np.mean(original_image != encrypted_image) * 100
    return npc_rate

def compute_uaci(original_image, encrypted_image):
    # Compute Unified Average Changing Intensity (UACI)
    uaci = np.mean(np.abs(original_image.astype(np.float64) - encrypted_image.astype(np.float64))) / 255 * 100
    return uaci

if __name__ == "__main__":
    # Load original and decrypted images
    original_image = io.imread('data/images/image.jpg', as_gray=True)
    decrypted_image = io.imread('data/images/decrypted_image.jpg', as_gray=True)

    # Compute metrics
    entropy = compute_entropy(original_image)
    histogram = compute_histogram(original_image)
    correlation = compute_correlation(original_image)
    energy = compute_energy(original_image)
    mse = compute_mse(original_image, decrypted_image)
    homogeneity = compute_homogeneity(original_image)
    npcr = compute_npcr(original_image, decrypted_image)
    uaci = compute_uaci(original_image, decrypted_image)

    # Print results
    print("Entropy:", entropy)
    print("Histogram:", histogram)
    print("Correlation:", correlation)
    print("Energy:", energy)
    print("Mean Square Error (MSE):", mse)
    print("Homogeneity:", homogeneity)
    print("Normalized Pixel Change Rate (NPCR):", npcr)
    print("Unified Average Changing Intensity (UACI):", uaci)
