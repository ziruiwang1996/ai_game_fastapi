import torch as tr
from .models import * 
from matplotlib import animation
import tempfile
import io
import os

def adjust_robot_arm(d:list, t:list):
    # Start joint angles at zero
    # Require gradient since joints will be optimized
    theta = tr.zeros(len(d), requires_grad=True)

    # Example target position for gripper in homogenous coordinates
    target = tr.tensor([[t[0], t[1], 1.]]).t()
    #target = tr.tensor([[50., 50., 1.]]).t()

    # Keep track of theta and error during descent
    history = []
    errors = []
    point_history = []

    # Visualize IK
    # 500 iterations of gradient descent
    # "loss" is squared distance between gripper and target
    # taking gradient of loss w.r.t joint angles
    for t in range(50):
        # Save current angles in history
        history.append(theta.clone().detach().numpy())

        # Forward kinematics for current arm position
        arm_points, grip_points = fwd(theta, d)
        point_history.append( (arm_points, grip_points) )

        # Gradient descent
        loss = ((arm_points[:,[-1]] - target)**2).sum()
        loss.backward()
        theta.data -= 0.004 * theta.grad # scale by learning rate
        theta.grad *= 0 # zero-out for next backward call

        errors.append(loss.item())

    # animate the state sequence
    def drawframe(n):
        arm_points, grip_points = point_history[n]
        pt.cla()
        pt.plot(target[0,0], target[1,0], 'ro')
        viz(arm_points, grip_points, d)
        pt.title("iter %d: loss = %f" % (n, errors[n]))

    # blit=True re-draws only the parts that have changed.
    fig = pt.figure(figsize=(3,3)) # each time-step is rendered on this figure
    anim = animation.FuncAnimation(fig, drawframe, frames=len(point_history), interval=500, blit=False)

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
        os.remove(temp_path)
    return buffer