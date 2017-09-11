import pid
import lowpass
import rospy
import tf

GAS_DENSITY = 2.858
ONE_MPH = 0.44704



class Controller(object):
    def __init__(self, decel_limit, accel_limit, max_steer_angle):
        self.decel_limit = decel_limit
        self.accel_limit = accel_limit
        self.max_steer_angle = max_steer_angle

        self.throttle_pid = pid.PID(kp = 0.7, ki = 0.005, kd = 0.3, mn=decel_limit, mx=accel_limit)
        self.throttle_filter = lowpass.LowPassFilter(tau = 0.0, ts = 1.0)

        self.steer_pid = pid.PID(kp = 3.0, ki = 0.0, kd = 0.0, mn=-max_steer_angle, mx=max_steer_angle)
        self.steer_filter = lowpass.LowPassFilter(tau = 0.0, ts = 1.0)

        self.clk = rospy.get_time()

    def control(self,
        target_linear_velocity,
        current_linear_velocity,
        target_angular_velocity,
        current_angular_velocity,
        dbw_enabled):
        # TODO: Change the arg, kwarg list to suit your needs
        # Return throttle, brake, steer

        t = rospy.get_time()
        dt = t - self.clk
        self.clk = t

        if not dbw_enabled:
            self.throttle_pid.reset()
            self.throttle_filter.ready = False
            self.steer_pid.reset()
            self.steer_filter.ready = False
            return 0.0, 0.0, 0.0

        rospy.loginfo("DBW_ENABLED!!!!")

        velocity_cte = target_linear_velocity - current_linear_velocity
        steer_cte = target_angular_velocity - current_angular_velocity

        rospy.loginfo('ctrl: steer_cte = {}, dt = {}'.format(steer_cte, dt))
        rospy.loginfo('ctrl: velocity_cte = {}, dt = {}'.format(velocity_cte, dt))


        # Steer PID
        steer = self.steer_pid.step(steer_cte, dt)
        rospy.loginfo('ctrl: steer = {}'.format(steer))
        steer = self.steer_filter.filt(steer)
        rospy.loginfo('ctrl: steer_filtered = {}'.format(steer))

        # Throtle PID
        throttle = self.throttle_pid.step(velocity_cte, dt)
        rospy.loginfo('ctrl: throttle = {}'.format(throttle))
        throttle = self.throttle_filter.filt(throttle)
        rospy.loginfo('ctrl: throttle_filtered = {}'.format(throttle))



        # steer = 0.0


        # Return throttle, brake, steer
        return throttle, 0., steer
