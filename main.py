import proto.messages_pb2 as messages_pb2

global max_duration, max_duration_name
max_duration = 0
max_duration_name = None

bytes_input = b'\n\x08\x08\x01\x18\x96\x01"\x01A\n\t\x08\x02\x10\x01\x18-"\x01B\n\t\x08\x03\x10\x01\x182"\x01C\n\t\x08\x04\x10\x02\x18\x14"\x01D\n\t\x08\x05\x10\x02\x18\x14"\x01E\x10\x01'


def request_to_response(serialized_input):

    def set_starting_step():
        if request.HasField("step_id"):
            for step in request.steps:
                if step.id == request.step_id:
                    starting_step = step
                    return starting_step
        else:
            for step in request.steps:
                if not step.HasField("parent_id"):
                    starting_step = step
                    return starting_step

    def children_count(parent):
        n = 0
        for step in steps:
            if step.parent_id == parent.id:
                n += 1
        return n

    def sort_by_dur(step):
        return int(step.duration)

    def calculate_duration(hierarchicalstep, step):
        children_duration = 0
        for child in hierarchicalstep.children:
            children_duration += int(child.duration)
        hierarchicalstep.children.sort(reverse=True, key=sort_by_dur)
        global max_duration, max_duration_name
        max_duration_loc = int(hierarchicalstep.duration) - children_duration
        if max_duration_loc >= max_duration:
            max_duration = max_duration_loc
            max_duration_name = step.name

    def add_children_and_calculate(hierarchicalstep, step):

        for index, childstep in steps_with_i.items():
            if childstep.parent_id == step.id:
                new_step = hierarchicalstep.children.add(name=childstep.name, duration=int(childstep.duration))
                new_parent = parents[childstep.id] = childstep
                add_children_and_calculate(new_step, new_parent)
            # Checking if parent has all of his children assigned
            if len(hierarchicalstep.children) == children_count(step):
                calculate_duration(hierarchicalstep, step)

        return messages_pb2.Response(
            hierarchical_step=hierarchicalstep,
            max_duration_step_name=max_duration_name,
            max_duration_step_duration=max_duration,
        )

    request = messages_pb2.Request.FromString(serialized_input)

    # Setting root step
    starting_step = set_starting_step()

    # Creating dicts to use as reference
    steps = request.steps
    steps_with_i = {step.id: step for step in steps}
    parents = {}

    # Setting root HierarchicalStep
    starting_hierarchicalstep_object = messages_pb2.Response().HierarchicalStep()
    starting_hierarchicalstep_object.name = starting_step.name
    starting_hierarchicalstep_object.duration = int(starting_step.duration)
    new_parent = parents[starting_step.id] = starting_step

    # Building structure and calculating parameters
    response = add_children_and_calculate(starting_hierarchicalstep_object, new_parent)
    response.max_duration_step_duration = max_duration
    return response.SerializeToString()


if __name__ == '__main__':
    print(request_to_response(bytes_input))