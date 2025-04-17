def calculate_hos_compliance(route_data, current_hours):
    """
    calculate hours of service compliance and necessary rest periods

    for property-carrying drivers
    - 11-hour driving limit: drive a max of 11 hours after 10 hours off duty
    - 14-hour limit: no driving beyond the 14th consecutive hour after coming on duty
    - 70-hour limit in 8 days: no driving after 70 hours on duty in 8 consecutive days
    """

    MAX_DRIVING_HOURS = 11.0
    MAX_ON_DUTY_HOURS = 14.0
    REQUIRED_REST_HOURS = 10.0
    MAX_WEEKLY_HOURS = 70.0
    WEEKLY_DAYS = 8

    # initialization of plan
    hos_plan = {
        "schedule": [],
        "rest_stops": [],
        "total_trip_days": 0
    }

    # starting with current hrs used
    hours_driven_today = 0
    hours_on_duty_today = current_hours
    total_hours_used = current_hours
    current_day = 1

    # hrs for the past 8 days
    daily_hours = [0] * WEEKLY_DAYS
    daily_hours[0] = current_hours

    # currently weekly hrs total
    weekly_hours_total = sum(daily_hours)

    # process each segment
    current_location = route_data["segments"][0]["from"]["address"]
    schedule = []

    # appending the initial status
    schedule.append({
        "day": current_day,
        "time": "00:00",  # this would be actual time in real app
        "status": "Start",
        "location": current_location,
        "hours_driven": hours_driven_today,
        "hours_on_duty": hours_on_duty_today,
        "weekly_hours": weekly_hours_total
    })

    # processing route segments with stops
    for i, segment in enumerate(route_data["segments"]):
        segment_hours = segment["duration"]
        driving_hours_remaining = MAX_DRIVING_HOURS - hours_driven_today
        on_duty_hours_remaining = MAX_ON_DUTY_HOURS - hours_on_duty_today
        weekly_hours_remaining = MAX_WEEKLY_HOURS - weekly_hours_total

        # check if any hos limit would be exceeded
        needs_rest = False
        rest_reason = ""

        if segment_hours > driving_hours_remaining:
            needs_rest = True
            rest_reason = "Exceeded 11-hour driving limit"
        elif segment_hours > on_duty_hours_remaining:
            needs_rest = True
            rest_reason = "Exceeded 14-hour on-duty limit"
        elif segment_hours > weekly_hours_remaining:
            needs_rest = True
            rest_reason = "Exceeded 70-hour/8-day limit"

        # if current segment is not possible to complete with the current hrs
        if needs_rest:
            # take a rest
            rest_location = current_location
            rest_stop = {
                "day": current_day,
                "location": rest_location,
                "duration": REQUIRED_REST_HOURS,
                "reason": f"Required 10-hour rest period: {rest_reason}"
            }
            hos_plan["rest_stops"].append(rest_stop)

            schedule.append({
                "day": current_day,
                "time": "--:--",  # placeholder
                "status": "Rest Start",
                "location": rest_location,
                "hours_driven": hours_driven_today,
                "hours_on_duty": hours_on_duty_today,
                "weekly_hours": weekly_hours_total
            })

            # increment day
            current_day += 1

            # shift daily hrs arr when new day starts
            daily_hours.pop()  # remove the oldest day
            daily_hours.insert(0, 0)  # add new day with zero hrs

            hours_driven_today = 0
            hours_on_duty_today = 0

            # recalculate weekly hrs total
            weekly_hours_total = sum(daily_hours)

            schedule.append({
                "day": current_day,
                "time": "00:00",  # placeholder
                "status": "Rest End",
                "location": rest_location,
                "hours_driven": hours_driven_today,
                "hours_on_duty": hours_on_duty_today,
                "weekly_hours": weekly_hours_total
            })

        # drive segment
        hours_driven_today += segment_hours
        hours_on_duty_today += segment_hours
        total_hours_used += segment_hours

        # update daily and weekly hrs
        daily_hours[0] += segment_hours
        weekly_hours_total = sum(daily_hours)

        current_location = segment["to"]["address"]

        schedule.append({
            "day": current_day,
            "time": "++:++",  # placeholder
            "status": "Driving",
            "location": current_location,
            "hours_driven": hours_driven_today,
            "hours_on_duty": hours_on_duty_today,
            "weekly_hours": weekly_hours_total
        })

        # check for stops after this segment
        if i < len(route_data["stops"]) and route_data["stops"][i]["type"] in ["pickup", "dropoff"]:
            stop = route_data["stops"][i]
            stop_duration = stop["duration"]

            # check if completeable within hos limit
            needs_rest_for_stop = False
            stop_rest_reason = ""

            if hours_on_duty_today + stop_duration > MAX_ON_DUTY_HOURS:
                needs_rest_for_stop = True
                stop_rest_reason = "Exceeded 14-hour on-duty limit"
            elif weekly_hours_total + stop_duration > MAX_WEEKLY_HOURS:
                needs_rest_for_stop = True
                stop_rest_reason = "Exceeded 70-hour/8-day limit"

            # if we need a rest break before stop
            if needs_rest_for_stop:
                rest_location = current_location
                rest_stop = {
                    "day": current_day,
                    "location": rest_location,
                    "duration": REQUIRED_REST_HOURS,
                    "reason": f"Required 10-hour rest period before stop: {stop_rest_reason}"
                }
                hos_plan["rest_stops"].append(rest_stop)

                schedule.append({
                    "day": current_day,
                    "time": "##:##",  # placeholder
                    "status": "Rest Start",
                    "location": rest_location,
                    "hours_driven": hours_driven_today,
                    "hours_on_duty": hours_on_duty_today,
                    "weekly_hours": weekly_hours_total
                })

                # increment day
                current_day += 1

                daily_hours.pop()
                daily_hours.insert(0, 0)

                hours_driven_today = 0
                hours_on_duty_today = 0


                weekly_hours_total = sum(daily_hours)

                schedule.append({
                    "day": current_day,
                    "time": "00:00",  # placeholder
                    "status": "Rest End",
                    "location": rest_location,
                    "hours_driven": hours_driven_today,
                    "hours_on_duty": hours_on_duty_today,
                    "weekly_hours": weekly_hours_total
                })

            # add the stop
            hours_on_duty_today += stop_duration
            total_hours_used += stop_duration

            # update daily and weekly hrs
            daily_hours[0] += stop_duration
            weekly_hours_total = sum(daily_hours)

            schedule.append({
                "day": current_day,
                "time": "**:**",  # placeholder
                "status": stop["type"].capitalize(),
                "location": current_location,
                "hours_driven": hours_driven_today,
                "hours_on_duty": hours_on_duty_today,
                "weekly_hours": weekly_hours_total
            })

    # address the fuel stops
    for fuel_stop in route_data["fuel_stops"]:
        fuel_stop_entry = {
            "day": current_day,  # placeholder
            "location": fuel_stop["estimated_location"],
            "duration": fuel_stop["duration"],
            "reason": "Fuel stop"
        }
        hos_plan["rest_stops"].append(fuel_stop_entry)

    # last schedule entry
    schedule.append({
        "day": current_day,
        "time": "@@:@@",  # placeholder
        "status": "End",
        "location": current_location,
        "hours_driven": hours_driven_today,
        "hours_on_duty": hours_on_duty_today,
        "weekly_hours": weekly_hours_total
    })

    hos_plan["schedule"] = schedule
    hos_plan["total_trip_days"] = current_day

    return hos_plan