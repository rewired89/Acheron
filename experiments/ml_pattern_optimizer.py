"""
Acheron ML Pattern Optimizer
=============================

Use machine learning to:
1. Predict which bioelectric patterns persist longest
2. Design optimal spatial encodings
3. Create error-correcting codes for bioelectric memory
4. Find patterns resistant to noise and perturbations

This is publishable research - combining bioelectricity + ML.

Approaches:
- Neural networks to predict persistence from initial voltage patterns
- Genetic algorithms to evolve optimal patterns
- Reinforcement learning to design encoding schemes

Author: Acheron Project
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
from simulations.bioelectric_persistence import PlanarianTissueModel
from encoder.bioelectric_encoder import BioelectricEncoder
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pickle


class PersistencePredictor(nn.Module):
    """
    Neural network that predicts pattern persistence from initial voltage distribution.

    Input: Flattened voltage grid (e.g., 30x30 = 900 values)
    Output: Predicted persistence ratio at 24 hours
    """

    def __init__(self, grid_size=(30, 30)):
        super().__init__()
        self.grid_size = grid_size
        input_dim = grid_size[0] * grid_size[1]

        # Architecture
        self.network = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.3),

            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.3),

            nn.Linear(128, 64),
            nn.ReLU(),

            nn.Linear(64, 1),
            nn.Sigmoid()  # Output between 0 and 1
        )

    def forward(self, x):
        # Flatten grid
        batch_size = x.shape[0]
        x_flat = x.view(batch_size, -1)
        return self.network(x_flat)


class MLPatternOptimizer:
    """
    Machine learning-based pattern optimization system.
    """

    def __init__(self, grid_size=(30, 30)):
        self.grid_size = grid_size
        self.encoder = BioelectricEncoder(grid_size=grid_size, cells_per_bit=9)
        self.predictor = None
        self.scaler = StandardScaler()

    def generate_training_data(self, n_samples=100):
        """
        Generate training data by simulating random patterns.

        Returns:
            patterns: List of voltage grids
            persistence_scores: List of persistence ratios
        """
        print("\n" + "="*70)
        print("GENERATING TRAINING DATA")
        print("="*70 + "\n")

        print(f"Generating {n_samples} random patterns...")
        print("(This will take several minutes)")
        print()

        patterns = []
        scores = []

        for i in range(n_samples):
            # Generate random binary string
            n_bits = np.random.randint(1, 16)  # 1 to 15 bits
            binary = ''.join(np.random.choice(['0', '1']) for _ in range(n_bits))

            # Encode
            voltage_grid = self.encoder.encode(binary)

            # Simulate
            tissue = PlanarianTissueModel(grid_size=self.grid_size, dt=1.0)
            tissue.V = voltage_grid.copy()

            # Quick simulation (6 hours for speed)
            tissue.run_persistence_test(duration_hours=6)

            # Record
            integrity = tissue.measure_bit_integrity()
            persistence_ratio = integrity['integrity_ratio']

            patterns.append(voltage_grid)
            scores.append(persistence_ratio)

            if (i + 1) % 10 == 0:
                print(f"Progress: {i+1}/{n_samples} ({(i+1)/n_samples*100:.0f}%)")

        print()
        print(f"✓ Generated {len(patterns)} training samples")
        print(f"  Mean persistence: {np.mean(scores):.3f}")
        print(f"  Std persistence: {np.std(scores):.3f}")
        print()

        return patterns, scores

    def train_predictor(self, patterns, scores, epochs=100):
        """
        Train neural network to predict persistence.
        """
        print("\n" + "="*70)
        print("TRAINING PERSISTENCE PREDICTOR")
        print("="*70 + "\n")

        # Convert to torch tensors
        X = np.array([p.flatten() for p in patterns])
        y = np.array(scores).reshape(-1, 1)

        # Normalize
        X_scaled = self.scaler.fit_transform(X)

        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )

        X_train = torch.FloatTensor(X_train).view(-1, *self.grid_size)
        X_test = torch.FloatTensor(X_test).view(-1, *self.grid_size)
        y_train = torch.FloatTensor(y_train)
        y_test = torch.FloatTensor(y_test)

        # Initialize model
        self.predictor = PersistencePredictor(self.grid_size)
        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.predictor.parameters(), lr=0.001)

        # Training loop
        train_losses = []
        test_losses = []

        print(f"Training for {epochs} epochs...")
        print()

        for epoch in range(epochs):
            # Train
            self.predictor.train()
            optimizer.zero_grad()
            outputs = self.predictor(X_train)
            loss = criterion(outputs, y_train)
            loss.backward()
            optimizer.step()

            # Test
            self.predictor.eval()
            with torch.no_grad():
                test_outputs = self.predictor(X_test)
                test_loss = criterion(test_outputs, y_test)

            train_losses.append(loss.item())
            test_losses.append(test_loss.item())

            if (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch+1}/{epochs}")
                print(f"  Train Loss: {loss.item():.4f}")
                print(f"  Test Loss:  {test_loss.item():.4f}")

        print()
        print("✓ Training complete!")
        print(f"  Final train loss: {train_losses[-1]:.4f}")
        print(f"  Final test loss:  {test_losses[-1]:.4f}")
        print()

        # Plot training curve
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(train_losses, label='Train Loss', linewidth=2)
        ax.plot(test_losses, label='Test Loss', linewidth=2)
        ax.set_xlabel('Epoch', fontsize=12, fontweight='bold')
        ax.set_ylabel('MSE Loss', fontsize=12, fontweight='bold')
        ax.set_title('Persistence Predictor Training', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('analysis/ml_training_curve.png', dpi=300, bbox_inches='tight')
        print("✓ Saved training curve: analysis/ml_training_curve.png")

        return train_losses, test_losses

    def predict_persistence(self, voltage_pattern):
        """
        Predict how long a pattern will persist (without simulation).
        """
        if self.predictor is None:
            raise ValueError("Model not trained yet! Call train_predictor() first.")

        self.predictor.eval()

        # Normalize
        X = voltage_pattern.flatten().reshape(1, -1)
        X_scaled = self.scaler.transform(X)
        X_tensor = torch.FloatTensor(X_scaled).view(1, *self.grid_size)

        # Predict
        with torch.no_grad():
            prediction = self.predictor(X_tensor)

        return prediction.item()

    def genetic_algorithm_optimizer(self, n_generations=50, population_size=20):
        """
        Use genetic algorithm to evolve optimal bioelectric patterns.

        Evolution:
        1. Start with random patterns
        2. Simulate and score each
        3. Select best performers
        4. Mutate and crossover
        5. Repeat

        Returns:
            Best pattern found
        """
        print("\n" + "="*70)
        print("GENETIC ALGORITHM PATTERN EVOLUTION")
        print("="*70 + "\n")

        print(f"Generations: {n_generations}")
        print(f"Population: {population_size}")
        print()

        # Initialize population
        population = []
        for _ in range(population_size):
            n_bits = np.random.randint(4, 12)
            binary = ''.join(np.random.choice(['0', '1']) for _ in range(n_bits))
            pattern = self.encoder.encode(binary)
            population.append((binary, pattern))

        best_scores = []

        for gen in range(n_generations):
            # Evaluate fitness
            fitness_scores = []
            for binary, pattern in population:
                # Use predictor if available (much faster)
                if self.predictor is not None:
                    score = self.predict_persistence(pattern)
                else:
                    # Simulate (slower)
                    tissue = PlanarianTissueModel(grid_size=self.grid_size, dt=2.0)
                    tissue.V = pattern.copy()
                    tissue.run_persistence_test(duration_hours=6)
                    score = tissue.measure_bit_integrity()['integrity_ratio']

                fitness_scores.append(score)

            # Track best
            best_idx = np.argmax(fitness_scores)
            best_scores.append(fitness_scores[best_idx])

            print(f"Generation {gen+1}/{n_generations}")
            print(f"  Best score: {fitness_scores[best_idx]:.3f}")
            print(f"  Mean score: {np.mean(fitness_scores):.3f}")
            print(f"  Pattern: {population[best_idx][0]}")

            # Selection (top 50%)
            sorted_indices = np.argsort(fitness_scores)[::-1]
            survivors = [population[i] for i in sorted_indices[:population_size // 2]]

            # Reproduction
            new_population = survivors.copy()

            while len(new_population) < population_size:
                # Crossover
                parent1, parent2 = np.random.choice(len(survivors), 2, replace=False)
                binary1, _ = survivors[parent1]
                binary2, _ = survivors[parent2]

                # Single-point crossover
                if len(binary1) > 0 and len(binary2) > 0:
                    point = min(len(binary1), len(binary2)) // 2
                    child = binary1[:point] + binary2[point:]
                else:
                    child = binary1

                # Mutation (flip random bit)
                if len(child) > 0 and np.random.random() < 0.1:
                    mut_idx = np.random.randint(len(child))
                    child = child[:mut_idx] + ('1' if child[mut_idx] == '0' else '0') + child[mut_idx+1:]

                # Encode
                try:
                    pattern = self.encoder.encode(child)
                    new_population.append((child, pattern))
                except:
                    pass  # Skip invalid patterns

            population = new_population[:population_size]

        print()
        print("✓ Evolution complete!")
        print(f"  Best pattern: {population[best_idx][0]}")
        print(f"  Best score: {best_scores[-1]:.3f}")
        print()

        # Plot evolution
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(best_scores, linewidth=2, marker='o')
        ax.set_xlabel('Generation', fontsize=12, fontweight='bold')
        ax.set_ylabel('Best Persistence Score', fontsize=12, fontweight='bold')
        ax.set_title('Genetic Algorithm Evolution', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('analysis/ml_genetic_evolution.png', dpi=300, bbox_inches='tight')
        print("✓ Saved evolution plot: analysis/ml_genetic_evolution.png")

        return population[best_idx]

    def save_model(self, path='experiments/persistence_predictor.pth'):
        """Save trained model."""
        if self.predictor is None:
            raise ValueError("No model to save!")

        torch.save({
            'model_state_dict': self.predictor.state_dict(),
            'scaler': self.scaler,
            'grid_size': self.grid_size
        }, path)
        print(f"✓ Model saved: {path}")

    def load_model(self, path='experiments/persistence_predictor.pth'):
        """Load trained model."""
        checkpoint = torch.load(path)
        self.grid_size = checkpoint['grid_size']
        self.scaler = checkpoint['scaler']
        self.predictor = PersistencePredictor(self.grid_size)
        self.predictor.load_state_dict(checkpoint['model_state_dict'])
        self.predictor.eval()
        print(f"✓ Model loaded: {path}")


def run_ml_optimization_pipeline():
    """
    Full ML optimization pipeline.
    """
    print("\n" + "="*70)
    print("ACHERON ML PATTERN OPTIMIZATION")
    print("="*70)

    optimizer = MLPatternOptimizer(grid_size=(30, 30))

    # Step 1: Generate training data
    print("\nStep 1: Generate training data")
    print("This will take ~10-20 minutes for 100 samples")
    confirm = input("Continue? (y/n): ").strip().lower()

    if confirm != 'y':
        print("Cancelled.")
        return

    patterns, scores = optimizer.generate_training_data(n_samples=50)  # Start small

    # Step 2: Train predictor
    print("\nStep 2: Train persistence predictor")
    optimizer.train_predictor(patterns, scores, epochs=100)

    # Save model
    optimizer.save_model()

    # Step 3: Genetic algorithm
    print("\nStep 3: Evolve optimal patterns with genetic algorithm")
    best_pattern = optimizer.genetic_algorithm_optimizer(n_generations=30, population_size=15)

    print("\n" + "="*70)
    print("OPTIMIZATION COMPLETE")
    print("="*70)
    print()
    print("Outputs:")
    print("  • analysis/ml_training_curve.png")
    print("  • analysis/ml_genetic_evolution.png")
    print("  • experiments/persistence_predictor.pth (saved model)")
    print()
    print(f"Best evolved pattern: {best_pattern[0]}")
    print()

    plt.show()


def quick_ml_demo():
    """
    Quick demo using pre-generated data (for testing).
    """
    print("\n" + "="*70)
    print("QUICK ML DEMO (Synthetic Data)")
    print("="*70)

    optimizer = MLPatternOptimizer(grid_size=(30, 30))

    # Generate small synthetic dataset
    print("\nGenerating 20 training samples...")
    patterns, scores = optimizer.generate_training_data(n_samples=20)

    # Train
    print("\nTraining predictor...")
    optimizer.train_predictor(patterns, scores, epochs=50)

    # Test prediction
    print("\nTesting prediction on new pattern...")
    test_pattern = optimizer.encoder.encode("10110")
    predicted_score = optimizer.predict_persistence(test_pattern)
    print(f"Predicted persistence: {predicted_score:.3f}")

    plt.show()


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        quick_ml_demo()
    else:
        run_ml_optimization_pipeline()
