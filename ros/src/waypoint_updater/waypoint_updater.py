#!/usr/bin/env python

import rospy
from geometry_msgs.msg import PoseStamped
from styx_msgs.msg import Lane, Waypoint

import math
import tf

'''
This node will publish waypoints from the car's current position to some `x` distance ahead.

As mentioned in the doc, you should ideally first implement a version which does not care
about traffic lights or obstacles.

Once you have created dbw_node, you will update this node to use the status of traffic lights too.

Please note that our simulator also provides the exact location of traffic lights and their
current status in `/vehicle/traffic_lights` message. You can use this message to build this node
as well as to verify your TL classifier.

TODO (for Yousuf and Aaron): Stopline location for each traffic light.
'''

LOOKAHEAD_WPS = 200 # Number of waypoints we will publish. You can change this number

dl = lambda a, b: math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2  + (a.z-b.z)**2)

def yaw_from_orientation(o):
    # https://answers.ros.org/question/69754/quaternion-transformations-in-python/
    q = (o.x, o.y, o.z, o.w)
    return tf.transformations.euler_from_quaternion(q)[2]

class WaypointUpdater(object):
    def __init__(self):
        rospy.init_node('waypoint_updater')

        rospy.Subscriber('/current_pose', PoseStamped, self.pose_cb)
        rospy.Subscriber('/base_waypoints', Lane, self.waypoints_cb)

        # TODO: Add a subscriber for /traffic_waypoint and /obstacle_waypoint below


        self.final_waypoints_pub = rospy.Publisher('final_waypoints', Lane, queue_size=1)

        # TODO: Add other member variables you need below
        self.waypoints = None

        self.cnt = 0

        rospy.spin()

    def dist_pose_waypoint(self, pose, waypoint):
        return dl(pose.pose.position, waypoint.pose.pose.position)

    def next_waypoint_idx(self, pose):
        dists = [self.dist_pose_waypoint(pose, wp) for wp in self.waypoints]
        closest_waypoint = dists.index(min(dists))

        wp = self.waypoints[closest_waypoint]

        wp_orientation = wp.pose.pose.orientation
        pose_orientation = pose.pose.orientation

        wp_yaw = yaw_from_orientation(wp_orientation)
        pose_yaw = yaw_from_orientation(pose_orientation)

        angle = math.atan2(wp.pose.pose.position.y-pose.pose.position.y, wp.pose.pose.position.x-pose.pose.position.x)
        rospy.loginfo('angle1 = {}'.format(angle))
        rospy.loginfo('pose_yaw = {}'.format(pose_yaw))
        delta = abs(pose_yaw-angle)
        while delta > math.pi: delta -= math.pi
        rospy.loginfo("delta1 = {}".format(delta))
        if (delta > math.pi/2):
            closest_waypoint += 1
            wp = self.waypoints[closest_waypoint]
            rospy.loginfo('forward')

        angle = math.atan2(wp.pose.pose.position.y-pose.pose.position.y, wp.pose.pose.position.x-pose.pose.position.x)
        delta = abs(pose_yaw-angle)
        while delta > math.pi: delta -= math.pi

        rospy.loginfo('angle = {}'.format(angle))
        rospy.loginfo("delta = {}".format(delta))
        rospy.loginfo('wp_yaw = {}'.format(wp_yaw))

    def pose_cb(self, pose):
        # TODO: Implement
        # rospy.loginfo('pose cb!!!!')
        # rospy.loginfo('Current pose = {}'.format(msg))
        if self.waypoints is None:
            rospy.loginfo('None waypoints')
            return

        # dists = [self.dist_pose_waypoint(pose, wp) for wp in self.waypoints]
        # closest_waypoint = dists.index(min(dists))

        log_out = (self.cnt % 100 == 0)

        # rospy.loginfo("one point = {}".format(self.waypoints[0]))

        # orientation = self.waypoints[closest_waypoint].pose.pose.orientation

        if log_out:
            self.next_waypoint_idx(pose)
            # rospy.loginfo("dist min = [{}] = {}".format(closest_waypoint, dists[closest_waypoint]))
            # rospy.loginfo("yaw = {}".format(yaw_from_orientation(orientation)))

        self.cnt += 1


    def waypoints_cb(self, waypoints):
        # TODO: Implement
        self.waypoints = waypoints.waypoints
        # rospy.loginfo('received waypoints len = {}'.format(len(waypoints.waypoints)))
        pass

    def traffic_cb(self, msg):
        # TODO: Callback for /traffic_waypoint message. Implement
        pass

    def obstacle_cb(self, msg):
        # TODO: Callback for /obstacle_waypoint message. We will implement it later
        pass

    def get_waypoint_velocity(self, waypoint):
        return waypoint.twist.twist.linear.x

    def set_waypoint_velocity(self, waypoints, waypoint, velocity):
        waypoints[waypoint].twist.twist.linear.x = velocity

    def distance(self, waypoints, wp1, wp2):
        dist = 0
        dl = lambda a, b: math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2  + (a.z-b.z)**2)
        for i in range(wp1, wp2+1):
            dist += dl(waypoints[wp1].pose.pose.position, waypoints[i].pose.pose.position)
            wp1 = i
        return dist


if __name__ == '__main__':
    try:
        WaypointUpdater()
    except rospy.ROSInterruptException:
        rospy.logerr('Could not start waypoint updater node.')
