from .models import Event, EventResponse


DEFAULT_EVENTS = (
    Event(
        name="Heavy snowfall",
        description="A strong snowfall disrupts transport and lowers temperature.",
        metric_deltas={"temperature": -8.0, "transport": -4.0},
        responses=(
            EventResponse("Emergency snow response", {"transport": 3.0}, 8.0),
            EventResponse("Temporary transport measures", {"transport": 2.0}, 5.0),
        ),
    ),
    Event(
        name="District heating accident",
        description="A heating network accident reduces winter resilience.",
        metric_deltas={"temperature": -5.0, "health": -2.0},
        responses=(EventResponse("Deploy repair crews", {"temperature": 3.0}, 7.0),),
    ),
    Event(
        name="Air quality decline",
        description="A sudden pollution spike affects public health.",
        metric_deltas={"air_quality": -6.0, "health": -3.0},
        responses=(EventResponse("Open clean-air shelters", {"health": 2.0}, 6.0),),
    ),
    Event(
        name="Major road closure",
        description="A major road is closed, increasing pressure on transport.",
        metric_deltas={"transport": -7.0, "economy": -2.0},
        responses=(EventResponse("Reroute public transport", {"transport": 4.0}, 9.0),),
    ),
)
