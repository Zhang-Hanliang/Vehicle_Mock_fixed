from lib.dsl import (
    create_behavior,
    create_event_trigger,
    create_set_action,
    mock_datapoint,
)
from lib.trigger import EventType

# json_path = os.getenv("MOCK_SIGNAL", "/home/dev/ws/mock/signals.json")

# with open(json_path, 'r') as f:
#     listOfSignals = json.load(f)

listOfSignals = [
    #{"signal": "Vehicle.Body.Lights.ExteriorLightControl", "value": [1, 2, 3]},
    {"signal": "Vehicle.Chassis.Accelerator.PedalPositionControl", "value": [1, 2]},
    {"signal": "Vehicle.Chassis.Brake.PedalPositionControl", "value": [1, 2]},
    {"signal": "Vehicle.Chassis.SteeringWheel.AngleControl", "value": [1, 2]},
    {"signal": "Vehicle.Powertrain.StartStop.StartControl", "value": [1, 2]},
]

for signal in listOfSignals:
    try:
        mock_datapoint(
            path=signal["signal"],
            initial_value=signal["value"],
            behaviors=[
                create_behavior(
                    trigger=create_event_trigger(EventType.ACTUATOR_TARGET),
                    action=create_set_action("$event.value"),
                )
            ],
        )
    except:
        print("Error occured with this signal")
        continue
