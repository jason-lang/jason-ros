#!/usr/bin/env python2
from hw_controller import *
import rospy
import argparse
import std_msgs.msg
import jason_msgs.msg

def arg_parser():
    parser = argparse.ArgumentParser(description="HardwareBridge node")

    parser.add_argument("-a","--action", help="Action manifest path", nargs=1, type=str)
    parser.add_argument("-p","--perception", help="Perception manifest path", nargs=1, type=str)

    args = vars(parser.parse_args())

    return args

def act(msg, args):
    action_controller = args[0]
    pub = args[1]

    action_status = jason_msgs.msg.ActionStatus()
    action_status.id = msg.header.seq

    action_status.result = action_controller.perform_action(msg.action_name, msg.parameters)

    pub.publish(action_status)


def main():
    print("Starting HwBridge node.")
    rospy.init_node('HwBridge')

    args = arg_parser()

    action_controller = ActionController()
    if args["action"] != None:
        action_controller.read_manifest(args["action"][0])
    else:
        action_controller.read_manifest()

    jason_actions_status_pub = rospy.Publisher(
    '/jason/actions_status',
    jason_msgs.msg.ActionStatus,
    queue_size=1,
    latch=False)

    jason_action_sub = rospy.Subscriber(
        '/jason/actions',
        jason_msgs.msg.Action,
        act, (action_controller,jason_actions_status_pub))


    perception_controller = PerceptionController()
    if args["perception"] != None:
        perception_controller.read_manifest(args["perception"][0])
    else:
        perception_controller.read_manifest()

    perception_controller.start_perceiving()

    jason_percepts_pub = rospy.Publisher(
    '/jason/percepts',
    jason_msgs.msg.Perception,
    queue_size=1,
    latch=False)

    rate = rospy.Rate(perception_controller.rate)
    while not rospy.is_shutdown():
        for p in perception_controller.perceptions.values():
            jason_percepts_pub.publish(p)

        rate.sleep()
    rospy.spin()

if __name__ == '__main__':
    main()
