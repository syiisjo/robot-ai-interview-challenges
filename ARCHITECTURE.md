# Architecture

```mermaid
flowchart LR
    EventSource --> RobotApplication
    RobotApplication --> Effect
    Effect --> RobotBridge
    RobotBridge --> ROS2
