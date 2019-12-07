from py.pyMover.goArm import GoArm
from py.pyMover.goCam import GoCam
from py.pyMover.problems import ProblemCollection
from py.helpers.myloggers import getLogger
from py.helpers.position import PositionHolder
from py.constants import goArmConsts as CONST
LOG = getLogger(__name__)


def not_implemented(cam):
    cam.respond(CONST.msg_NOT_IMPLEMENTED)


def put_a_problem(arm, problems, cam, level):
    cam.respond(CONST.msg_OK)
    try:
        cam.request(CONST.com_HOLD)
        problem = problems.get_next_problem(int(level))
        LOG.info("Got the problem for you. Playing")
        arm.put_stones(problem)
    except Exception as e:
        LOG.error("Oops, failure putting a position: {}".format(e))
    finally:
        arm.set_position(arm.cam_position)
        cam.request(CONST.com_RESUME)


def main():
    arm = GoArm()
    cam = GoCam()
    arm.cam = cam
    cam.arm = arm

    ph = PositionHolder()
    problems = ProblemCollection()

    arm.set_position(arm.cam_position)

    while True:
        try:
            message = cam.message
            if message and message.type == CONST.msg_t_REQUEST:
                # processing here
                if message.cmd == CONST.com_Problem:
                    put_a_problem(arm, problems, cam, message.body or 1)
                elif message.cmd == CONST.com_Play:
                    not_implemented(cam)
                elif message.cmd == CONST.com_TeachMe:
                    not_implemented(cam)
                elif message.cmd == CONST.com_Calib:
                    not_implemented(cam)
                elif message.cmd == CONST.com_Fin:
                    arm.disconnect()
                    cam.disconnect()
                    break
            else:
                ph.position = cam.snap()
                # could do stretching or some other attractive action here
        except Exception as e:
            LOG.error("Exception running the main module: {}".format(e))


if __name__ == "__main__":
    main()
