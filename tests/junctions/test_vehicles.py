from junctions.vehicles import Vehicles


def test_add_vehicle():
    # GIVEN vehicles state class
    vehicles = Vehicles()

    # WHEN I add a vehicle
    label = vehicles.add_vehicle()

    # THEN I get a generated label back
    assert label == "vehicle1"
    # ... and the label is in the list of vehicles
    assert vehicles.vehicle_labels() == (label,)
    # ... and we have an inactive vehicle in the set
    assert not vehicles.vehicle(label).is_active
