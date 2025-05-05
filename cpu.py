import numpy as np
import matplotlib.pyplot as plt


def generate_buddhabrot(
    width=800, height=600, samples=1_000_000, max_iter=1000, escape_radius=2.0
):
    # Define the region in the complex plane
    x_min, x_max = -2.0, 1.0
    y_min, y_max = -1.5, 1.5

    # Initialize the histogram
    histogram = np.zeros((height, width), dtype=np.longlong)

    # Iterate through random c samples
    for _ in range(samples):
        z = complex(0.0, 0)
        c = complex(np.random.uniform(x_min, x_max), np.random.uniform(y_min, y_max))
        orbit = []
        escaped = False
        # Track orbit until escape or max iterations
        for _ in range(max_iter):
            z = z * z + c
            orbit.append(z)
            if abs(z) > escape_radius:
                escaped = True
                break

        if not escaped:
            # Increment histogram for each point in the orbit
            for z in orbit:
                x = int((z.real - x_min) / (x_max - x_min) * width)
                y = int((z.imag - y_min) / (y_max - y_min) * height)
                if 0 <= x < width and 0 <= y < height:
                    histogram[y, x] += 1

    print(np.max(histogram))

    # Log scaling for contrast
    log_hist = np.log1p(histogram)

    # Plot
    plt.figure(figsize=(10, 7.5))
    plt.imshow(log_hist, extent=(x_min, x_max, y_min, y_max), origin="lower")
    plt.axis("off")
    plt.title("Buddhabrot (1 000 000 samples)")
    plt.show()


# Generate and display Buddhabrot with 1 million samples
generate_buddhabrot(width=800, height=600, samples=100000, max_iter=1000)
