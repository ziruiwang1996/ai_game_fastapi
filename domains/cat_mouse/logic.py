import numpy as np
from .models import CatMouseDomain
from matplotlib import animation
import matplotlib.pyplot as pt
import tempfile
import io
import os

"""
Using TD Q learning when probabilities and optimal utilities are not accessible
ɣ Discount factor: numbers closer to 1 put more emphasis on future rewards
"""
def TD_Q_Learning(game:CatMouseDomain, ɣ = 0.5):
    N, K = game.N, game.K
    # Initial Q estimates and counts
    Q = np.zeros((N, K)) # Repeatedly updated during TD learning

    choice_counts = np.zeros((N, K)) # How many times each action was done in each state
    display_period = 30000 # number of time-steps between visualizations
    display_window = 10 # how long to animate the animals each visualization

    # Arbitrary initial state when learning begins
    state = (0, 0, 3, 0)

    # Total number of time-steps for learning
    num_timesteps = 10**5

    fig, ax = pt.subplots(figsize=(8, 8))
    frames = []

    for t in range(num_timesteps):
        # Get current state index and update visit count
        i = game.state_to_index(state)
        # Choose an action
        # Uniformly at random if exploring
        # Best current Q estimate if optimizing
        k = np.random.randint(K) 
        # Update the action count and perform the chosen action
        choice_counts[i, k] += 1
        mdx, mdy = game.actions[k]
        state = game.move(state, mdx, mdy)
        # TD update rule
        # α is the state-dependent learning rate, should get smaller over time
        # j is the new state index after the current action is performed
        α = 1./choice_counts[i,k]
        j = game.state_to_index(state)
        Q[i,k] = (1-α) * Q[i,k] + α * (game.r[i] + ɣ * Q[j,:].max())
        # Visualize progress
        if False or (t % display_period < display_window):
            frames.append(state)

    def update(frame_idx):
        ax.clear()
        state = frames[frame_idx]
        game.plot_state(state)
        ax.set_title(f"Time-step {frame_idx}")

    anim = animation.FuncAnimation(fig, update, frames=len(frames), interval=200, blit=False)

    with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as temp_file:
        temp_path = temp_file.name 
    try:
        anim.save(temp_path, writer="pillow")
        buffer = io.BytesIO()
        with open(temp_path, "rb") as f:
            buffer.write(f.read())
        buffer.seek(0) 
    except Exception as e:
        print(f"Error saving GIF: {e}")
    finally:
        os.remove(temp_path)  # Delete the temp file
    return buffer