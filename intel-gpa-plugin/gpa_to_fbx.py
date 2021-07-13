import json
from os import path
import sys
from os import path

COMPONENT_TYPE_BYTE = 5120
COMPONENT_TYPE_UNSIGNED_BYTE = 5121
COMPONENT_TYPE_SHORT = 5122
COMPONENT_TYPE_UNSIGNED_SHORT = 5123
COMPONENT_TYPE_INT = 5124
COMPONENT_TYPE_UNSIGNED_INT = 5125
COMPONENT_TYPE_FLOAT = 5126
COMPONENT_TYPE_DOUBLE = 5130

def getTypes(format):
    if format == 'R32G32B32_FLOAT':
        return (COMPONENT_TYPE_FLOAT, 'VEC3')
    if format == 'R8G8B8A8_SNORM':
        return (COMPONENT_TYPE_UNSIGNED_BYTE, 'VEC4')
    if format == 'R32G32_FLOAT':
        return (COMPONENT_TYPE_FLOAT, 'VEC2')
    if format == 'B8G8R8A8_UNORM':
        return (COMPONENT_TYPE_UNSIGNED_BYTE, 'VEC4')
    if format == 'R8G8B8A8_UINT':
        return (COMPONENT_TYPE_UNSIGNED_INT, 'VEC4')

def process_gpa_json(filename):
    dir_name = path.dirname(filename)
    gltf_obj = {
        'buffers': [],
        'accessors': [],
        'bufferViews': [],
        'meshes': [],
        'nodes': [],
        'scene': 0,
        "scenes": [
            {
                'nodes': [0]
            }
        ],
    }

    with open(filename) as f:
        data = json.load(f)
        resource_id_mapper = {}
        idx = 0
        for input in data['inputs']:
            if input['view_type'] == 'VBV' or input['view_type'] == 'IBV':
                resource_id = input['resource_id']
                gltf_obj['buffers'].append({
                    'uri': '%s/%d.bin' % (input['view_type'], resource_id),
                    'byteLength': input['size'],
                    'stride': input['stride']
                })

                resource_id_mapper[input['resource_id']] = idx
                idx += 1

        view_id = 0
        for vertex_buffer in data['metadata']['input_geometry']['vertex_buffers']:
            buffer_id = resource_id_mapper[vertex_buffer['buffer']]
            for layout in vertex_buffer['layouts']:
                name = layout['name']
                format = layout['format']

                gltf_obj['bufferViews'].append({
                    'buffer': buffer_id,
                    'offset': layout['offset'],
                    'byteLength': gltf_obj['buffers'][buffer_id]['byteLength'],
                })

                (componentType, type) = getTypes(format)
                gltf_obj['accessors'].append({
                    'bufferView': view_id,
                    'componentType': componentType,
                    'count': 2549,
                    'type': type
                })

                view_id += 1


    with open(filename + '.gltf', 'w') as f:
        f.write(json.dumps(gltf_obj, indent=4))

if __name__ == '__main__':
    gpa_json = 'd:/dump/178.json'
    if len(sys.argv) > 1:
        gpa_json = sys.argv[1]    
    process_gpa_json(gpa_json)