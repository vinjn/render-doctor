# The obj dumped from GPA lacks texcoord, hence use this script to add texcoords
# openmesh cheatsheet https://gist.github.com/zishun/0ba4f7925a1cd1ece890eb4dee4cd81e

import openmesh
import struct

uv_float_idx = 0

def process_mesh(in_bin_filename, in_obj_filename, out_filename):
    global uv_float_idx
    uv_float_idx = 0
    uv_floats = []
    def add_uv_float(number):
        global uv_float_idx
        if uv_float_idx % 4 < 2:
            uv_floats.append(number)
        uv_float_idx += 1
    mesh = openmesh.read_trimesh(in_obj_filename, vertex_normal = True)
    for fh in mesh.faces():
        # print(fh.idx())
        pass

    with open(in_bin_filename, 'rb') as f:
        word = f.read(4)
        while word:
            result = struct.unpack('f', word)[0]
            add_uv_float(result)
            # print(result)
            word = f.read(4)

    print('n_faces: ', mesh.n_faces())
    print('n_vertices: ', mesh.n_vertices())
    print('uv_floats: ', len(uv_floats) / 2)

    for i in range(mesh.n_vertices()):
        vh0 = mesh.vertex_handle(i)
        mesh.set_texcoord2D(vh0, (uv_floats[i*2], uv_floats[i*2+1]))

    openmesh.write_mesh(out_filename, mesh, vertex_normal = True, vertex_tex_coord=True)

# process_mesh('d:/dump/VBV/4169.bin', '../ggs/sol-body.obj', '../ggs/sol-body-with-uv.obj')
# process_mesh('d:/dump/VBV/4551.bin', '../ggs/sol-head.obj', '../ggs/sol-head-uv.obj')
process_mesh('d:/dump/VBV/8671.bin', '../ggs/chipp/head.obj', '../ggs/chipp/head-uv.obj')
process_mesh('d:/dump/VBV/7995.bin', '../ggs/chipp/body.obj', '../ggs/chipp/body-uv.obj')
