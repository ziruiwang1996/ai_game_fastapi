import matplotlib.pyplot as pt
import torch as tr

# Visualize the current arm/gripper position
def viz(arm_points, grip_points, d):

    arm_points = arm_points.detach() # for matplotlib
    grip_points = grip_points.detach() # for matplotlib

    # arm_points[0,j], arm_points[1,j] are (x,y) coordinates for joint j
    # similarly the points delineating the gripper
    pt.plot(arm_points[0,:], arm_points[1,:], '-ko')
    pt.plot(grip_points[0,:], grip_points[1,:], '-k')

    pt.xlim([-sum(d), sum(d)])
    pt.ylim([-sum(d), sum(d)])

# Get transformation matrices for position/orientation of each joint
# In transformation matrix M, M[:2,:2] is the rotation and M[:2,3] is the translation
def get_transforms(theta, d):
    # theta[j] is angle for joint j (tr.tensor)
    # d[j] is the length of the link connected to joint j (np.array)
    # theta is tr.tensor so that IK can use gradient descent

    # to avoid writing out sin/cos a lot
    s = tr.sin(theta)
    c = tr.cos(theta)

    # First transformation (base link) is at the origin, so identity matrix
    # 3x3 for homogenous coordinates
    transforms = [tr.eye(3)]

    # Construct remaining transformations for each joint
    for j in range(len(theta)):

        # Translation matrix
        T = tr.tensor([
            [1., 0., d[j]],
            [0., 1., 0.  ],
            [0., 0., 1.  ]])
        # Rotation matrix
        R = tr.eye(3)
        R[0,0] =  c[j]
        R[0,1] = -s[j]
        R[1,0] =  s[j]
        R[1,1] =  c[j]
        # Compose rotation and translation for current joint relative to previous joint
        M = tr.mm(R, T)

        # Compose with transforms from previous joints to get relative to origin
        transforms.append(tr.mm(transforms[j], M))

    return transforms

# Forward kinematics: use transforms to get positions of each joint/gripper
def fwd(theta, d):

    # Get transforms for current joints
    transforms = get_transforms(theta, d)

    # Extract coordinates of each joint
    # arm_points[:,j] is cartesian position of j^th joint
    origin = tr.tensor([[0., 0., 1.]]).t()
    arm_points = tr.cat([tr.mm(M, origin) for M in transforms], dim=1)

    # Extract points at gripper knuckles and tips
    grip_points = tr.tensor([
        [1.,  1., 1.], # left fingertip
        [0.,  1., 1.], # left knuckle
        [0., -1., 1.], # right knuckle
        [1., -1., 1.], # right fingertip
    ]).t()
    grip_points = tr.mm(transforms[-1], grip_points)

    return arm_points, grip_points



# fig = pt.figure(figsize=(4,4)) # each time-step is rendered on this figure

# Fixed lengths for each link in arm
d = [8., 13.]

# Start joint angles at zero
# Require gradient since joints will be optimized
theta = tr.zeros(len(d), requires_grad=True)

# Example target position for gripper in homogenous coordinates
target = tr.tensor([[3., 8., 1.]]).t()
#target = tr.tensor([[50., 50., 1.]]).t()

# Keep track of theta and error during descent
history = []
errors = []
point_history = []

# Visualize IK
# 500 iterations of gradient descent
# "loss" is squared distance between gripper and target
# taking gradient of loss w.r.t joint angles
for t in range(100):

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

    # # this way of animating too choppy
    # if t % 5 == 0:
    #   # Visualize current arm position and error
    #   pt.cla()
    #   pt.plot(target[0,0], target[1,0], 'ro')
    #   viz(arm_points, grip_points, d)
    #   pt.title("iter %d: loss = %f" % (t, loss))

    #   # Boiler-plate code for the animation
    #   display.display(fig) # Display the current figure content
    #   display.clear_output(wait=True) # don't clear it until new content is ready

print("Animating...")
# animate the state sequence
def drawframe(n):
  arm_points, grip_points = point_history[n]
  pt.cla()
  pt.plot(target[0,0], target[1,0], 'ro')
  viz(arm_points, grip_points, d)
  pt.title("iter %d: loss = %f" % (n, errors[n]))

from matplotlib import animation

# blit=True re-draws only the parts that have changed.
fig = pt.figure(figsize=(3,3)) # each time-step is rendered on this figure
anim = animation.FuncAnimation(fig, drawframe, frames=len(point_history), interval=500, blit=False)
pt.show()