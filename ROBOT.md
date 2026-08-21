
# Report

## Completed

- Implemented Event and Effect models.
- Implemented greeting, farewell timeout and duplicate suppression.
- Added pytest coverage.
- Added snapshot isolation.

## Test Command

```bash
pytest -q

- `ros2 action info` reports one action client and zero action servers.
- `/get_robot_mode` returned `STAND`.
- `robot-action.service` is inactive.

### Inference

`accepted_async` only means the request was accepted by the submitting layer or queued asynchronously. It does not prove that the robot completed the waving action.

The most likely problem is in the execution layer: the action server is unavailable, or the robot action service is not running.

### Next Checks

1. Check why `robot-action.service` is inactive.
2. Check service logs with `journalctl`.
3. Confirm the expected ROS 2 action server is launched.
4. Run `ros2 action list` and inspect the exact action type.
5. Submit a test request only after an action server is available.
6. Verify feedback and final result from the action client.
7. Confirm physical execution on the robot.

### Can a Real Action Be Executed Now?

No. There are zero action servers and the robot action service is inactive. The request must not be treated as completed.
