import csv
import random
import math

# Set seed for reproducibility
random.seed(42)

# Channel list
channels = ["FidNz", "FidT9", "FidT10"] + [f"E{i}" for i in range(1, 257)]

# Subjects
subjects = [f"sub-{i:02d}" for i in range(1, 21)]

# Conditions
conditions = ["pre", "post"]

# Define frontal channels (E1-E40 approximately for GSN-HydroCel-256)
frontal_channels = set([f"E{i}" for i in range(1, 41)])


def gauss(mu=0, sigma=1.0):
    """Generate Gaussian random number using Box-Muller transform"""
    u1 = random.random()
    u2 = random.random()
    mag = sigma * math.sqrt(-2.0 * math.log(u1 + 1e-10))
    z0 = mag * math.cos(2 * math.pi * u2)
    return mu + z0


def generate_with_effect():
    """Generate data with frontal alpha power increase (20-30% increase in post)"""
    rows = []
    for subject in subjects:
        # Subject-specific baseline variation
        subject_offset = gauss(0, 0.5)

        for channel in channels:
            # Channel-specific noise
            channel_noise = gauss(0, 0.3)

            for condition in conditions:
                # Base alpha power (6-12 range)
                base_value = random.uniform(6.5, 11.5)
                value = base_value + subject_offset + channel_noise

                # Apply frontal effect for post condition (20-30% increase)
                if condition == "post" and channel in frontal_channels:
                    effect_size = random.uniform(1.20, 1.30)  # 20-30% increase
                    value *= effect_size

                # Ensure values stay in realistic range
                value = max(5.0, min(14.0, value))

                rows.append([subject, channel, condition, round(value, 4)])
    return rows


def generate_no_effect():
    """Generate pure random noise around baseline (7-8 range)"""
    rows = []
    for subject in subjects:
        for channel in channels:
            for condition in conditions:
                # Pure random noise around 7-8 range
                value = random.uniform(6.5, 8.5)
                # Add small gaussian noise
                value += gauss(0, 0.2)
                # Ensure values stay in range
                value = max(6.0, min(9.0, value))

                rows.append([subject, channel, condition, round(value, 4)])
    return rows


def write_csv(filepath, rows):
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["subject", "channel", "condition", "value"])
        writer.writerows(rows)


# Generate and save files
print("Generating example_with_effect_256.csv...")
with_effect_data = generate_with_effect()
write_csv(
    "/Users/idohaber/00_development/eegtopo/example_with_effect_256.csv",
    with_effect_data,
)
print(f"  Saved {len(with_effect_data)} rows")

print("Generating example_no_effect_256.csv...")
no_effect_data = generate_no_effect()
write_csv(
    "/Users/idohaber/00_development/eegtopo/example_no_effect_256.csv", no_effect_data
)
print(f"  Saved {len(no_effect_data)} rows")

# Verify files - calculate means manually
print("\nVerification:")
print(f"  With effect - first 5 rows:")
for row in with_effect_data[:5]:
    print(f"    {row}")

print(f"\n  No effect - first 5 rows:")
for row in no_effect_data[:5]:
    print(f"    {row}")

# Check effect in with_effect file
print("\n  Checking frontal effect in 'with_effect' data:")
pre_frontal = [r[3] for r in with_effect_data if r[1] == "E1" and r[2] == "pre"]
post_frontal = [r[3] for r in with_effect_data if r[1] == "E1" and r[2] == "post"]
pre_mean = sum(pre_frontal) / len(pre_frontal)
post_mean = sum(post_frontal) / len(post_frontal)
print(f"    E1 pre mean: {pre_mean:.2f}")
print(f"    E1 post mean: {post_mean:.2f}")
print(f"    Increase: {((post_mean / pre_mean) - 1) * 100:.1f}%")

print("\nDone!")
