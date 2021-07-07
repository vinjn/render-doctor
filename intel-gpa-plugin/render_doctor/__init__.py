import json
import os
import plugin_api

#
def IsUsefulInput(viewtype):
    return viewtype == "CBV" or viewtype == "IBV" or viewtype == "VBV" or viewtype == "SRV"

def DumpBufferByDrawcall(folder, call, res, id, texture):
    if not os.path.exists(folder):
        os.mkdir(folder)

    buffer = None
    if texture == False:
        buffer = res.get_buffer_data(call, True)
    else:
        buffer = res.get_image_data(0, 0, call, True)
    
    file = open((folder + "{}.bin").format(id), "wb")
    file.write(bytearray(buffer.data))
    file.close()

def DumpBufferByResource(folder, call, res, id, type, texture):
    fdir = (folder + "\\{}\\").format(type)
    if not os.path.exists(fdir):
        os.mkdir(fdir)

    fname = (fdir + "{}.bin").format(id)
    if os.path.exists(fname):
        return

    buffer = None
    if texture == True:
        buffer = res.get_image_data(0, 0, call, True)
    else:
        buffer = res.get_buffer_data(call, True)

    file = open(fname, "wb")
    file.write(bytearray(buffer.data))
    file.close()

#
def run(start, end, dir:"Output Foloder"="d:\\dump", debug:"For debug"=0):
    # Get api_log and metrics for further work
    api_log_accessor = plugin_api.get_api_log_accessor()
    metrics_accessor = plugin_api.get_metrics_accessor()

    if os.path.exists(dir):
        ROOT_FOLDER = dir
    else:
        raise RuntimeError("Error: Output directory is NOT exist.")

    count = 0
    calls = api_log_accessor.get_calls()
    for call in calls:
        apicall = call.get_description()
        if apicall["is_event"] == True:
            count = count + 1

            # only care drawIndexed and drawIndexedInstanced
            if  (apicall["name"] == "DrawIndexedInstanced" or apicall["name"] == "DrawIndexed") and count >= start and count <= end:
                file = open((ROOT_FOLDER + "\\{}.json").format(count), "w")
                folder = (ROOT_FOLDER + "\\{}\\").format(count)

                bindings = call.get_bindings()

                file.write(json.dumps(call.get_description()))
                file.write('\n')

                file.write(json.dumps(bindings["metadata"]))
                file.write('\n')

                # dump textures and cbv/vbv/ibv
                for v in bindings["inputs"]:
                    desc = v.get_description()
                    if IsUsefulInput(desc["view_type"]) == True:
                        if debug == 1:
                            DumpBufferByDrawcall(folder, call, v, desc["resource_id"], desc["resource_type"] == "texture")
                        else:
                            DumpBufferByResource(ROOT_FOLDER, call, v, desc["resource_id"], desc["view_type"], desc["resource_type"] == "texture")
                        file.write(json.dumps(desc))
                        file.write('\n')

                # execution = bindings["execution"]
                # file.write(json.dumps(execution["program"].get_description()))
                # file.write(execution["program"].get_il_source("vertex", "isa"))

                file.close()

#
def desc():
    return {
        "name": "DumpRawData",
        "description": "The plugin can dump mesh and textures.",
        "apis": ["DirectX"],
        "applicabilities": ["Apilog"],
        "plugin_api_version": "1.0"
    }
