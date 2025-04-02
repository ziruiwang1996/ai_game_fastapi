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